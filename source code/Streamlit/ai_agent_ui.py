# ai_agent_ui.py
import streamlit as st
import datetime

st.title("📅 AI Study Planner Agent")

tasks = []
with st.form("task_form"):
    name = st.text_input("Task name")
    duration = st.number_input("Duration (minutes)", min_value=10, step=10)
    importance = st.slider("Importance (1 = low, 5 = high)", 1, 5, 3)
    deadline = st.date_input("Deadline (optional)", value=None)
    submitted = st.form_submit_button("Add Task")
    if submitted and name:
        tasks.append({"name": name, "duration": duration, "importance": importance, "deadline": deadline})

if st.button("Generate Schedule"):
    available_hours = 8
    available_minutes = available_hours * 60
    today = datetime.date.today()
    tasks.sort(key=lambda t: (-t["importance"], t["deadline"] or today))

    schedule = []
    current_time = datetime.datetime.now().replace(hour=9, minute=0)

    for task in tasks:
        if task["duration"] <= available_minutes:
            start = current_time
            end = start + datetime.timedelta(minutes=task["duration"])
            schedule.append((task["name"], start.strftime("%H:%M"), end.strftime("%H:%M")))
            current_time = end
            available_minutes -= task["duration"]

    st.subheader("✅ Today's Plan")
    for name, start, end in schedule:
        st.write(f"{start} - {end}: {name}")
