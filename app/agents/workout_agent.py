import json
from app.services.prompt_loader import render_prompt
from app.services.llm_client import llm_client
from app.models.plan_schema import WorkoutPlan


def _extract_json(raw: str) -> str:
    """Strip markdown code fences if the LLM adds them despite instructions."""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return raw.strip()


def workout_agent_node(state: dict) -> dict:
    """
    LangGraph node: generates a 6-day + rest workout plan as structured JSON,
    validated against WorkoutPlan schema. Writes result into state["workout_plan"].
    On failure, state["workout_plan"] is set to None and state["workout_plan_error"]
    holds the error message.
    """
    prompt = render_prompt(
        "workout_agent.jinja",
        name=state["name"],
        age=state["age"],
        gender=state["gender"],
        height_cm=state["height_cm"],
        weight_kg=state["weight_kg"],
        bmi=state["bmi"],
        bmi_category=state["bmi_category"],
        activity_level=state["activity_level"],
        goal=state["goal"],
        workout_preference=state["workout_preference"],
        medical=state.get("medical"),
    )

    state["workout_plan"] = None
    state["workout_plan_error"] = None

    try:
        raw_response = llm_client.generate(prompt)
    except RuntimeError as e:
        state["workout_plan_error"] = f"LLM call failed: {e}"
        return state

    try:
        clean_json = _extract_json(raw_response)
        parsed = json.loads(clean_json)
        workout_plan = WorkoutPlan(**parsed)
        state["workout_plan"] = workout_plan.model_dump()
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        state["workout_plan_error"] = f"Failed to parse workout plan JSON: {e}"

    return state