from datetime import date
from app.models.user_profile import Gender, ActivityLevel, UserProfile


ACTIVITY_MULTIPLIERS = {
    ActivityLevel.sedentary: 1.2,
    ActivityLevel.light: 1.375,
    ActivityLevel.moderate: 1.55,
    ActivityLevel.active: 1.725,
    ActivityLevel.very_active: 1.9,
}


class CalculationError(Exception):
    """Raised when a fitness calculation fails due to invalid input."""
    pass


def calculate_age(dob: date) -> int:
    """Calculate age in years from date of birth."""
    today = date.today()
    if dob > today:
        raise CalculationError("Date of birth cannot be in the future.")
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age <= 0 or age > 120:
        raise CalculationError(f"Calculated age ({age}) is out of valid range.")
    return age


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate Body Mass Index (kg/m^2)."""
    if height_cm <= 0 or weight_kg <= 0:
        raise CalculationError("Height and weight must be positive values.")
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: Gender) -> float:
    """Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation."""
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender == Gender.male:
        bmr = base + 5
    elif gender == Gender.female:
        bmr = base - 161
    else:
        bmr = base - 78
    if bmr <= 0:
        raise CalculationError("Calculated BMR is invalid (<= 0). Check input values.")
    return round(bmr, 2)


def calculate_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    """Calculate Total Daily Energy Expenditure from BMR and activity level."""
    if activity_level not in ACTIVITY_MULTIPLIERS:
        raise CalculationError(f"Unknown activity level: {activity_level}")
    return round(bmr * ACTIVITY_MULTIPLIERS[activity_level], 2)


def get_bmi_category(bmi: float) -> str:
    """Classify BMI into standard WHO categories."""
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_all(profile: UserProfile) -> dict:
    """
    Run all fitness calculations for a given UserProfile.
    Raises CalculationError on any invalid intermediate result.
    """
    age = calculate_age(profile.date_of_birth)
    bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
    bmr = calculate_bmr(profile.weight_kg, profile.height_cm, age, profile.gender)
    tdee = calculate_tdee(bmr, profile.activity_level)

    return {
        "age": age,
        "bmi": bmi,
        "bmi_category": get_bmi_category(bmi),
        "bmr": bmr,
        "tdee": tdee,
    }