# ai_agent.py
import datetime

def get_tasks():
    tasks = []
    print("Enter your tasks (type 'done' when finished):")
    while True:
        name = input("Task name: ")
        if name.lower() == "done":
            break
        duration = int(input("Duration (in minutes): "))
        importance = int(input("Importance (1-5): "))
        deadline = input("Deadline (YYYY-MM-DD, or leave blank): ")
        deadline = deadline if deadline else None
        tasks.append({"name": name, "duration": duration, "importance": importance, "deadline": deadline})
    return tasks

def plan_schedule(tasks, available_hours=8):
    available_minutes = available_hours * 60
    today = datetime.date.today()

    # Reasoning: sort by (importance desc, deadline asc)
    tasks.sort(key=lambda t: (-t["importance"], t["deadline"] or str(today)))
    
    schedule = []
    current_time = datetime.datetime.now().replace(hour=9, minute=0)  # Start 9 AM
    
    for task in tasks:
        if task["duration"] <= available_minutes:
            start = current_time
            end = start + datetime.timedelta(minutes=task["duration"])
            schedule.append((task["name"], start.strftime("%H:%M"), end.strftime("%H:%M")))
            current_time = end
            available_minutes -= task["duration"]
    return schedule

def main():
    print("📅 AI Study Planner Agent")
    tasks = get_tasks()
    schedule = plan_schedule(tasks)
    print("\n✅ Today's Plan:")
    for name, start, end in schedule:
        print(f"{start} - {end}: {name}")

if __name__ == "__main__":
    main()
