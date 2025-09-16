# multi_agent_rag_ui.py
import streamlit as st
import datetime
import time

# -------------------------
# Knowledge Base (Simulated RAG)
# -------------------------
KNOWLEDGE_BASE = {
    "machine learning": "Machine learning is the study of algorithms that improve from experience.",
    "compiler design": "A compiler translates source code into executable machine code.",
    "networking": "Computer networks enable devices to communicate and share resources.",
    "data structures": "Common data structures include arrays, linked lists, stacks, and queues."
}

def retrieve_notes(query):
    for key, value in KNOWLEDGE_BASE.items():
        if key in query.lower():
            return value
    return "No relevant notes found."

# -------------------------
# Agents
# -------------------------
class PlannerAgent:
    def __init__(self, available_hours=8, start_hour=9):
        self.available_hours = available_hours
        self.start_hour = start_hour

    def plan(self, tasks):
        available_minutes = self.available_hours * 60
        today = datetime.date.today()
        tasks.sort(key=lambda t: (-t["importance"], t.get("deadline", today)))
        current_time = datetime.datetime.now().replace(hour=self.start_hour, minute=0, second=0, microsecond=0)

        schedule = []
        for task in tasks:
            if task["duration"] <= available_minutes:
                start = current_time
                end = start + datetime.timedelta(minutes=task["duration"])
                schedule.append({"name": task["name"], "start": start, "end": end})
                current_time = end
                available_minutes -= task["duration"]
            else:
                schedule.append({"name": task["name"] + " (BACKLOG)", "start": None, "end": None})
        return schedule

class ExecutorAgent:
    def execute(self, schedule, placeholder):
        for task in schedule:
            if task["start"]:
                placeholder.write(f"▶ Starting: **{task['name']}** at {task['start'].strftime('%H:%M')}")
                note = retrieve_notes(task['name'])
                placeholder.write(f"📖 Study Note: {note}")
                time.sleep(1)
                placeholder.write(f"✅ Finished: **{task['name']}** at {task['end'].strftime('%H:%M')}")
            else:
                placeholder.write(f"⏭ Skipping backlog task: **{task['name']}**")
                time.sleep(0.5)

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(page_title="Study Planner with RAG", layout="centered")
st.title("🤖 Multi-Agent Planner + RAG Notes")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

with st.form("task_form", clear_on_submit=True):
    name = st.text_input("Task name")
    duration = st.number_input("Duration (minutes)", min_value=5, step=5, value=30)
    importance = st.slider("Importance (1 = low, 5 = high)", 1, 5, 3)
    deadline = st.date_input("Deadline (optional)")
    submitted = st.form_submit_button("Add Task")
    if submitted and name:
        st.session_state.tasks.append({
            "name": name,
            "duration": int(duration),
            "importance": int(importance),
            "deadline": deadline if deadline else None
        })

st.subheader("📝 Current Tasks")
if st.session_state.tasks:
    for i, t in enumerate(st.session_state.tasks):
        st.write(f"{i+1}. {t['name']} — {t['duration']} mins — importance {t['importance']} — deadline {t['deadline']}")
else:
    st.write("No tasks yet. Add tasks above.")

if st.button("Generate Schedule"):
    planner = PlannerAgent()
    schedule = planner.plan(st.session_state.tasks)
    st.session_state.schedule = schedule
    st.subheader("📅 Planned Schedule")
    for t in schedule:
        if t["start"]:
            st.write(f"{t['start'].strftime('%H:%M')} - {t['end'].strftime('%H:%M')}: {t['name']}")
        else:
            st.write(f"BACKLOG: {t['name']}")

if st.button("Run Executor Agent"):
    if "schedule" in st.session_state:
        executor = ExecutorAgent()
        st.subheader("⚡ Execution Log")
        placeholder = st.empty()
        executor.execute(st.session_state.schedule, placeholder)
    else:
        st.warning("Please generate a schedule first.")
