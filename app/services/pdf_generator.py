from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm


def generate_plan_pdf(profile_data: dict, indices: dict, diet_plan: dict,
                       workout_plan: dict, output_path: str) -> str:
    """
    Builds a PDF report from profile summary, calculated indices,
    structured diet_plan (DietPlan.model_dump()) and workout_plan
    (WorkoutPlan.model_dump()). Returns the output_path on success.
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                             topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], fontSize=20)
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    # --- Section 1: Profile Summary ---
    story.append(Paragraph("Fitness & Diet Plan Report", title_style))
    story.append(Spacer(1, 12))

    profile_table_data = [
        ["Name", profile_data["name"]],
        ["Age", str(indices["age"])],
        ["Gender", profile_data["gender"]],
        ["Location", profile_data["location"]],
        ["Height (cm)", str(profile_data["height_cm"])],
        ["Weight (kg)", str(profile_data["weight_kg"])],
        ["BMI", f"{indices['bmi']} ({indices['bmi_category']})"],
        ["BMR (kcal)", str(indices["bmr"])],
        ["TDEE (kcal)", str(indices["tdee"])],
        ["Goal", profile_data["goal"]],
        ["Food Preference", profile_data["food_preference"]],
        ["Workout Preference", profile_data["workout_preference"]],
        ["Medical Notes", profile_data.get("medical") or "None"],
    ]
    profile_table = Table(profile_table_data, colWidths=[5 * cm, 10 * cm])
    profile_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#2E4053")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(profile_table)
    story.append(PageBreak())

    # --- Section 2: Diet Plan (7 days) ---
    story.append(Paragraph("7-Day Diet Plan", title_style))
    story.append(Spacer(1, 12))

    if diet_plan:
        for day in diet_plan["days"]:
            story.append(Paragraph(f"Day {day['day']}", heading_style))
            for slot_key, slot_label in [
                ("breakfast", "Breakfast"), ("lunch", "Lunch"),
                ("evening_snack", "Evening Snack"), ("dinner", "Dinner")
            ]:
                story.append(Paragraph(slot_label, styles["Heading3"]))
                rows = [["Option", "Food Items", "Approx. Kcal"]]
                for opt in day[slot_key]:
                    rows.append([
                        str(opt["option_number"]),
                        Paragraph(opt["food_items"], normal_style),
                        str(opt["approx_kcal"]),
                    ])
                t = Table(rows, colWidths=[2 * cm, 10 * cm, 3 * cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5DADE2")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(t)
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 12))
    else:
        story.append(Paragraph("Diet plan unavailable.", normal_style))

    story.append(PageBreak())

    # --- Section 3: Workout Plan (6 days + rest) ---
    story.append(Paragraph("Weekly Workout Plan", title_style))
    story.append(Spacer(1, 12))

    if workout_plan:
        for day in workout_plan["days"]:
            story.append(Paragraph(f"Day {day['day']} - {day['focus']}", heading_style))
            if day["is_rest"] or not day["exercises"]:
                story.append(Paragraph("Rest day. Light stretching optional.", normal_style))
            else:
                rows = [["Exercise", "Sets/Reps/Duration", "Why"]]
                for ex in day["exercises"]:
                    rows.append([
                        Paragraph(ex["name"], normal_style),
                        ex["sets_reps_or_duration"],
                        Paragraph(ex["why"], normal_style),
                    ])
                t = Table(rows, colWidths=[5 * cm, 4 * cm, 6 * cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#58D68D")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]))
                story.append(t)
            story.append(Spacer(1, 10))
    else:
        story.append(Paragraph("Workout plan unavailable.", normal_style))

    doc.build(story)
    return output_path