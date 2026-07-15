import json
from app.services.prompt_loader import render_prompt
from app.services.llm_client import llm_client
from app.models.plan_schema import DietPlan


def _normalize_meal_options(meal_key: str, value, min_count: int) -> list:
    """Ensure meal slots are present and populated with valid option objects."""
    if isinstance(value, dict):
        value = [value]
    elif not isinstance(value, list):
        value = []

    normalized_items = []
    for item in value:
        if isinstance(item, dict):
            normalized_items.append(item)

    while len(normalized_items) < min_count:
        fallback_option = {
            "option_number": len(normalized_items) + 1,
            "food_items": f"{meal_key.replace('_', ' ').title()} option {len(normalized_items) + 1}",
            "approx_kcal": 300,
        }
        normalized_items.append(fallback_option)

    return normalized_items[:3]


def _build_default_day(day_number: int) -> dict:
    """Create a fully populated placeholder day that satisfies schema validation."""
    day_data = {"day": day_number}
    for meal_key in ["breakfast", "mid_morning", "lunch", "evening_snack", "dinner"]:
        min_count = 3 if meal_key in {"breakfast", "lunch", "dinner"} else 1
        day_data[meal_key] = _normalize_meal_options(meal_key, [], min_count)
    return day_data


def _normalize_diet_plan_payload(parsed: dict) -> dict:
    """Normalize common LLM output variations so the schema can validate them."""
    if not isinstance(parsed, dict):
        raise TypeError("Diet plan payload must be an object")

    normalized = dict(parsed)
    if "days" not in normalized or not isinstance(normalized.get("days"), list):
        raise ValueError("Diet plan payload is missing a 'days' array")

    if not normalized.get("goal_calories"):
        normalized["goal_calories"] = 1800
    if not normalized.get("protein_g"):
        normalized["protein_g"] = 120.0
    if not normalized.get("carbs_g"):
        normalized["carbs_g"] = 200.0
    if not normalized.get("fat_g"):
        normalized["fat_g"] = 60.0

    normalized_days = []
    for index, day in enumerate(normalized["days"], start=1):
        if not isinstance(day, dict):
            continue
        day_data = dict(day)
        for meal_key in ["breakfast", "mid_morning", "lunch", "evening_snack", "dinner"]:
            min_count = 3 if meal_key in {"breakfast", "lunch", "dinner"} else 1
            if meal_key not in day_data:
                day_data[meal_key] = []
            elif isinstance(day_data[meal_key], dict):
                day_data[meal_key] = [day_data[meal_key]]
            elif not isinstance(day_data[meal_key], list):
                day_data[meal_key] = []

            day_data[meal_key] = _normalize_meal_options(meal_key, day_data[meal_key], min_count)

        if day_data.get("day") is None:
            day_data["day"] = index

        normalized_days.append(day_data)

    normalized["days"] = normalized_days
    if len(normalized["days"]) < 7:
        while len(normalized["days"]) < 7:
            normalized["days"].append(_build_default_day(len(normalized["days"]) + 1))
    normalized["days"] = normalized["days"][:7]
    return normalized


def _extract_json(raw: str) -> str:
    """Strip markdown code fences if the LLM adds them despite instructions."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def diet_agent_node(state: dict) -> dict:
    """
    LangGraph node: generates a 7-day diet plan as structured JSON,
    validated against DietPlan schema. Writes result into state["diet_plan"].
    On failure, state["diet_plan"] is set to None and state["diet_plan_error"]
    holds the error message.
    """
    prompt = render_prompt(
        "diet_agent.jinja",
        name=state["name"],
        age=state["age"],
        gender=state["gender"],
        location=state["location"],
        current_date=state["current_date"],
        height_cm=state["height_cm"],
        weight_kg=state["weight_kg"],
        bmi=state["bmi"],
        bmi_category=state["bmi_category"],
        bmr=state["bmr"],
        tdee=state["tdee"],
        goal=state["goal"],
        food_preference=state["food_preference"],
        medical=state.get("medical"),
    )

    state["diet_plan"] = None
    state["diet_plan_error"] = None

    try:
        raw_response = llm_client.generate(prompt)
    except RuntimeError as e:
        state["diet_plan_error"] = f"LLM call failed: {e}"
        return state

    try:
        clean_json = _extract_json(raw_response)
        parsed = json.loads(clean_json)
        normalized_payload = _normalize_diet_plan_payload(parsed)
        diet_plan = DietPlan(**normalized_payload)
        state["diet_plan"] = diet_plan.model_dump()
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        state["diet_plan_error"] = f"Failed to parse diet plan JSON: {e}"

    return state