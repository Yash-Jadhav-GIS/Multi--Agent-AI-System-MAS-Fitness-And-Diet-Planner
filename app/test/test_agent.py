from app.agents.diet_agent import diet_agent_node
from app.agents.workout_agent import workout_agent_node

state = {
    "name": "Yash", "age": 27, "gender": "male",
    "height_cm": 175, "weight_kg": 70,
    "bmi": 22.86, "bmi_category": "Normal",
    "bmr": 1673.75, "tdee": 2594.31,
    "activity_level": "moderate", "goal": "lose_weight",
    "medical": None,
}

state = diet_agent_node(state)
state = workout_agent_node(state)

print("DIET PLAN:\n", state["diet_plan"])
print("\nWORKOUT PLAN:\n", state["workout_plan"])