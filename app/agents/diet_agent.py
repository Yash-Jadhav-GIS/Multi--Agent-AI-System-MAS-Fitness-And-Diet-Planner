import json
from app.services.prompt_loader import render_prompt
from app.services.llm_client import llm_client
from app.models.plan_schema import DietPlan


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
        diet_plan = DietPlan(**parsed)
        state["diet_plan"] = diet_plan.model_dump()
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        state["diet_plan_error"] = f"Failed to parse diet plan JSON: {e}"

    return state