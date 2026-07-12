import os
import uuid
from datetime import date
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.user_profile import UserProfile
from app.services.calc import calculate_all, CalculationError
from app.agents.graph import plan_graph
from app.services.pdf_generator import generate_plan_pdf

router = APIRouter(prefix="/api", tags=["fitness"])


@router.post(
    "/calculate",
    summary="Calculate BMI, BMR, TDEE for a user profile",
    description="Takes a validated UserProfile and returns computed fitness indices "
                "(age, BMI, BMI category, BMR, TDEE). Returns 400 if inputs produce "
                "an invalid calculation, 422 if the input itself fails validation.",
)
def calculate(profile: UserProfile):
    try:
        result = calculate_all(profile)
    except CalculationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal calculation error.")
    return {"profile": profile.name, "results": result}


def _build_state(profile: UserProfile, indices: dict) -> dict:
    """Shared helper: builds the LangGraph input state from profile + calculated indices."""
    return {
        "name": profile.name,
        "age": indices["age"],
        "gender": profile.gender.value,
        "location": profile.location,
        "current_date": str(date.today()),
        "height_cm": profile.height_cm,
        "weight_kg": profile.weight_kg,
        "bmi": indices["bmi"],
        "bmi_category": indices["bmi_category"],
        "bmr": indices["bmr"],
        "tdee": indices["tdee"],
        "activity_level": profile.activity_level.value,
        "goal": profile.goal.value,
        "food_preference": profile.food_preference.value,
        "workout_preference": profile.workout_preference,
        "medical": profile.medical,
    }


@router.post(
    "/generate-plan",
    summary="Generate full 7-day diet + 6-day workout plan",
    description="Runs the full pipeline: calculates BMI/BMR/TDEE, then generates a "
                "structured 7-day diet plan and 6-day workout plan (+1 rest day) via "
                "LLM agents. Returns partial results if one agent fails.",
)
def generate_plan(profile: UserProfile):
    try:
        indices = calculate_all(profile)
    except CalculationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    state = _build_state(profile, indices)

    try:
        result = plan_graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}")

    if result["diet_plan"] is None and result["workout_plan"] is None:
        raise HTTPException(
            status_code=502,
            detail=f"Both agents failed. Diet: {result['diet_plan_error']}, "
                   f"Workout: {result['workout_plan_error']}"
        )

    return {
        "profile": profile.name,
        "indices": indices,
        "diet_plan": result["diet_plan"],
        "diet_plan_error": result["diet_plan_error"],
        "workout_plan": result["workout_plan"],
        "workout_plan_error": result["workout_plan_error"],
    }


@router.post(
    "/generate-plan-pdf",
    summary="Generate full plan and return as downloadable PDF",
    description="Same as /generate-plan, but returns the result rendered as a PDF file.",
)
def generate_plan_pdf_endpoint(profile: UserProfile):
    try:
        indices = calculate_all(profile)
    except CalculationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    state = _build_state(profile, indices)

    try:
        result = plan_graph.invoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plan generation failed: {e}")

    if result["diet_plan"] is None and result["workout_plan"] is None:
        raise HTTPException(status_code=502, detail="Both agents failed to generate plans.")

    os.makedirs("generated_pdfs", exist_ok=True)
    filename = f"generated_pdfs/plan_{uuid.uuid4().hex[:8]}.pdf"

    profile_data = {
        "name": profile.name, "gender": profile.gender.value, "location": profile.location,
        "height_cm": profile.height_cm, "weight_kg": profile.weight_kg,
        "goal": profile.goal.value, "food_preference": profile.food_preference.value,
        "workout_preference": profile.workout_preference, "medical": profile.medical,
    }

    generate_plan_pdf(profile_data, indices, result["diet_plan"], result["workout_plan"], filename)

    return FileResponse(filename, media_type="application/pdf", filename="fitness_diet_plan.pdf")