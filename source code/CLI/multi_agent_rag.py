# multi_agent_rag.py
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
# Planner Agent
# -------------------------
class PlannerAgent:
    def __init__(self, available_hours=8, start_hour=9):
        self.available_hours = available_hours
        self.start_hour = start_hour

    def plan(self, tasks):
        available_minutes = self.available_hours * 60
        current_time = datetime.datetime.now().replace(hour=self.start_hour, minute=0, second=0, microsecond=0)

        tasks.sort(key=lambda t: (-t["importance"], t.get("deadline", datetime.date.max)))
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

# -------------------------
# Executor Agent
# -------------------------
class ExecutorAgent:
    def execute(self, schedule):
        for task in schedule:
            if task["start"]:
                print(f"▶ Starting: {task['name']} at {task['start'].strftime('%H:%M')}")
                note = retrieve_notes(task['name'])
                print(f"📖 Study Note: {note}")
                time.sleep(1)  # Simulated execution
                print(f"✅ Finished: {task['name']} at {task['end'].strftime('%H:%M')}")
            else:
                print(f"⏭ Skipping backlog task: {task['name']}")

# -------------------------
# Main CLI
# -------------------------
if __name__ == "__main__":
    tasks = [
        {"name": "Study Machine Learning", "duration": 60, "importance": 5, "deadline": datetime.date.today()},
        {"name": "Review Compiler Design", "duration": 45, "importance": 4, "deadline": datetime.date.today()},
        {"name": "Practice Networking", "duration": 30, "importance": 3, "deadline": None},
    ]

    planner = PlannerAgent()
    schedule = planner.plan(tasks)

    print("\n📅 Planned Schedule")
    for t in schedule:
        if t["start"]:
            print(f"{t['start'].strftime('%H:%M')} - {t['end'].strftime('%H:%M')}: {t['name']}")
        else:
            print(f"BACKLOG: {t['name']}")

    print("\n⚡ Running Executor Agent...")
    executor = ExecutorAgent()
    executor.execute(schedule)
