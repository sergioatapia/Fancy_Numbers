#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def read_number():
    with open('number.txt', 'r') as f:
        return int(f.read().strip())

def write_number(num):
    with open('number.txt', 'w') as f:
        f.write(str(num))

def git_commit():
    subprocess.run(['git', 'add', 'number.txt'])
    date = datetime.now().strftime('%Y-%m-%d') 
    commit_message = f"Update number: {date}"
    subprocess.run(['git', 'commit', '-m', commit_message])

def git_push():
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)
        
        
def tasks_already_scheduled_for_today():
    # Get today's date in YYYY_MM_DD format
    today = datetime.now().strftime("%Y_%m_%d")

    # Check if tasks are already sceduled for the day, from the date in the task name
    result = subprocess.run(["schtasks", "/query", "/fo", "LIST"], capture_output=True, text=True)
    return today in result.stdout

def update_scheduler_with_random_times():
    # Check if tasks for today are already scheduled
    if tasks_already_scheduled_for_today():
        print("Tasks for today are already scheduled. Skipping task creation.")
        return

    # Generate random times for the day
    num_times = random.randint(2, 10)
    times = set()

    while len(times) < num_times:
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        times.add((hour, minute))

    # Path to the batch file
    bat_file_path = os.path.join(script_dir, "update_number_tasks.bat")

    # Today's date for unique task names
    today = datetime.now().strftime("%Y_%m_%d")

    # Write commands to the batch file
    with open(bat_file_path, "w") as bat_file:
        for hour, minute in sorted(times):
            time_string = f"{hour:02d}:{minute:02d}"
            task_name = f"UpdateNumber_{today}_{hour}_{minute}"
            command = (
                f'schtasks /create /tn "{task_name}" '
                f'/tr "python {os.path.join(script_dir, "update_number.py")}" /sc ONCE /st {time_string}\n'
            )
            bat_file.write(command)

    print(f"Task Scheduler commands written to {bat_file_path}. Run this file to schedule tasks.")

def main():
    try:
        current_number = read_number()
        new_number = current_number + 1
        write_number(new_number)

        git_commit()
        git_push()

        update_scheduler_with_random_times()

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()