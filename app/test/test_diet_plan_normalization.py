from app.agents.diet_agent import _normalize_diet_plan_payload
from app.models.plan_schema import DietPlan


def test_normalize_diet_plan_payload_fills_missing_summary_fields():
    payload = {
        "days": [
            {
                "day": 1,
                "breakfast": [{"option_number": 1, "food_items": "Oats", "approx_kcal": 350}],
                "mid_morning": [{"option_number": 1, "food_items": "Fruit", "approx_kcal": 100}],
                "lunch": [{"option_number": 1, "food_items": "Rice bowl", "approx_kcal": 500}],
                "evening_snack": [{"option_number": 1, "food_items": "Yogurt", "approx_kcal": 150}],
                "dinner": [{"option_number": 1, "food_items": "Paneer curry", "approx_kcal": 500}],
            }
        ]
    }

    normalized = _normalize_diet_plan_payload(payload)
    plan = DietPlan(**normalized)

    assert plan.goal_calories > 0
    assert plan.protein_g > 0
    assert plan.carbs_g > 0
    assert plan.fat_g > 0
    assert len(plan.days) == 7


def test_normalize_diet_plan_payload_fills_empty_meal_slots():
    payload = {
        "days": [
            {
                "day": 1,
                "breakfast": [],
                "mid_morning": [],
                "lunch": [],
                "evening_snack": [],
                "dinner": [],
            }
        ]
    }

    normalized = _normalize_diet_plan_payload(payload)
    plan = DietPlan(**normalized)

    assert len(plan.days[0].breakfast) == 3
    assert len(plan.days[0].mid_morning) == 1
    assert len(plan.days[0].lunch) == 3
    assert len(plan.days[0].evening_snack) == 1
    assert len(plan.days[0].dinner) == 3
