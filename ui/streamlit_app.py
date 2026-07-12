import streamlit as st
import requests
from datetime import date

API_BASE = "http://127.0.0.1:5000/api"

st.set_page_config(page_title="AI Fitness & Diet Planner", page_icon="💪")
st.title("💪 AI Fitness & Diet Planner")
st.caption("Enter your details to get a personalized 7-day diet and workout plan.")

with st.form("profile_form"):
    name = st.text_input("Name")
    dob = st.date_input("Date of birth", min_value=date(1920, 1, 1), max_value=date.today())
    gender = st.selectbox("Gender", ["male", "female", "other"])
    location = st.text_input("Location (city)")
    height_cm = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
    weight_kg = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=70.0)
    body_fat_pct = st.number_input("Body fat % (optional)", min_value=0.0, max_value=60.0, value=0.0)
    medical = st.text_area("Medical conditions / allergies (optional)")
    activity_level = st.selectbox(
        "Activity level", ["sedentary", "light", "moderate", "active", "very_active"]
    )
    goal = st.selectbox("Goal", ["lose_weight", "maintain", "gain_weight"])
    food_preference = st.selectbox("Food preference", ["veg", "non_veg", "eggetarian"])
    workout_preference = st.text_input("Workout preference (e.g. gym, yoga, running, mixed)")

    submitted = st.form_submit_button("Generate My Plan")

if submitted:
    payload = {
        "name": name,
        "date_of_birth": str(dob),
        "gender": gender,
        "location": location,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "body_fat_pct": body_fat_pct if body_fat_pct > 0 else None,
        "medical": medical if medical else None,
        "activity_level": activity_level,
        "goal": goal,
        "food_preference": food_preference,
        "workout_preference": workout_preference,
    }
    st.session_state["payload"] = payload

if "payload" in st.session_state:
    payload = st.session_state["payload"]

    with st.spinner("Generating your personalized plan..."):
        try:
            response = requests.post(f"{API_BASE}/generate-plan", json=payload, timeout=90)
            response.raise_for_status()
            data = response.json()

            st.subheader("📊 Your Indices")
            st.json(data["indices"])

            if data["diet_plan"]:
                st.subheader("🥗 Diet Plan (Day 1 preview)")
                st.json(data["diet_plan"]["days"][0])
            else:
                st.warning(f"Diet plan issue: {data['diet_plan_error']}")

            if data["workout_plan"]:
                st.subheader("🏋️ Workout Plan (Day 1 preview)")
                st.json(data["workout_plan"]["days"][0])
            else:
                st.warning(f"Workout plan issue: {data['workout_plan_error']}")

            st.divider()
            st.subheader("📄 Download Full Report")

            with st.spinner("Preparing PDF..."):
                pdf_response = requests.post(f"{API_BASE}/generate-plan-pdf", json=payload, timeout=90)
                pdf_response.raise_for_status()

            st.download_button(
                label="⬇️ Download PDF Report",
                data=pdf_response.content,
                file_name="fitness_diet_plan.pdf",
                mime="application/pdf",
            )

        except requests.exceptions.HTTPError as e:
            try:
                detail = e.response.json().get("detail", "Unknown error")
            except Exception:
                detail = str(e)
            st.error(f"Server error: {detail}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not reach the API: {e}")