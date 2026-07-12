from app.services.prompt_loader import render_prompt

prompt = render_prompt(
    "workout_agent.jinja",
    name="Yash", age=27, gender="male", height_cm=175, weight_kg=70,
    bmi=22.86, bmi_category="Normal", activity_level="moderate",
    goal="lose_weight", medical=None
)
print(prompt)