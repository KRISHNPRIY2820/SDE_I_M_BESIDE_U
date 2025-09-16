# multi_agent.py
import datetime
import time

class PlannerAgent:
    def __init__(self, available_hours=8, start_hour=9):
        self.available_hours = available_hours
        self.start_hour = start_hour

    def plan(self, tasks):
        available_minutes = self.available_hours * 60
        today = datetime.date.today()

        def deadline_key(t):
            if t["deadline"]:
                return datetime.datetime.strptime(t["deadline"], "%Y-%m-%d").date()
            return datetime.date.max

        tasks.sort(key=lambda t: (-t["importance"], deadline_key(t)))
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
    def execute(self, schedule):
        print("\n▶ Executor Agent starting execution...\n")
        for task in schedule:
            if task["start"]:
                print(f"Starting: {task['name']} at {task['start'].strftime('%H:%M')}")
                # Simulate execution with sleep (fast-forward, not real minutes)
                time.sleep(1)
                print(f"Finished: {task['name']} at {task['end'].strftime('%H:%M')}\n")
            else:
                print(f"Skipping backlog task: {task['name']}")


def main():
    tasks = [
        {"name": "Math Homework", "duration": 60, "importance": 5, "deadline": "2025-09-20"},
        {"name": "Read Notes", "duration": 30, "importance": 3, "deadline": None},
        {"name": "Lab Report", "duration": 90, "importance": 4, "deadline": "2025-09-18"},
    ]

    planner = PlannerAgent()
    executor = ExecutorAgent()

    schedule = planner.plan(tasks)
    print("✅ Planned Schedule:")
    for t in schedule:
        if t["start"]:
            print(f"{t['start'].strftime('%H:%M')} - {t['end'].strftime('%H:%M')}: {t['name']}")
        else:
            print(f"BACKLOG: {t['name']}")

    executor.execute(schedule)


if __name__ == "__main__":
    main()
