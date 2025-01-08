#!/usr/bin/env python3
import os
import sys
import random
import subprocess
import png
import argparse
from datetime import datetime, date, timedelta

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)


def read_number():
    with open('number.txt', 'r') as f:
        return int(f.read().strip())


def write_number(num):
    with open('number.txt', 'w') as f:
        f.write(str(num))


def git_commit():
    # Stage the changes
    subprocess.run(['git', 'add', 'number.txt'])

    # Create commit with current date
    date = datetime.now().strftime('%Y-%m-%d')
    commit_message = f"Update number: {date}"
    subprocess.run(['git', 'commit', '-m', commit_message])


def git_push():
    # Push the committed changes to GitHub
    result = subprocess.run(['git', 'push'], capture_output=True, text=True)
    if result.returncode == 0:
        print("Changes pushed to GitHub successfully.")
    else:
        print("Error pushing to GitHub:")
        print(result.stderr)


def update_cron_with_random_time():
    # Generate random hour (0-23) and minute (0-59)
    random_hour = random.randint(0, 23)
    random_minute = random.randint(0, 59)

    # Define the new cron job command
    new_cron_command = f"{random_minute} {random_hour} * * * cd {script_dir} && python3 {os.path.join(script_dir, 'update_number.py')} {' '.join(sys.argv[1:])}\n"

    # Get the current crontab
    cron_file = "/tmp/current_cron"
    os.system(f"crontab -l > {cron_file} 2>/dev/null || true")  # Save current crontab, or create a new one if empty

    # Update the crontab file
    with open(cron_file, "r") as file:
        lines = file.readlines()

    with open(cron_file, "w") as file:
        for line in lines:
            # Remove existing entry for `update_number.py` if it exists
            if "update_number.py" not in line:
                file.write(line)
        # Add the new cron job at the random time
        file.write(new_cron_command)

    # Load the updated crontab
    os.system(f"crontab {cron_file}")
    os.remove(cron_file)

    print(f"Cron job updated to run at {random_hour}:{random_minute} tomorrow.")


def update_on_this_day(image_filename, the_day):
    r = png.Reader(image_filename)
    img = r.read()

    if img[1] != 7:
        return False

    # Which row/col of the image will we need?
    (day_of_year, week_day, week_number) = map(int, the_day.strftime('%-j %w %U').split())
    image_row = week_day

    # we always want to start rendering the image in the first, complete, week of the year
    # So, either:
    # a) it starts on a Sunday (week_day = 0) and day_of year is 1-indexed
    if week_day + 1 == day_of_year:
        image_column = 0

    # Or we're already in the second week
    elif week_number > 0:
        image_column = week_number - 1

    # Or we're in the first few days of an incomplete week
    else:
        return False

    # img[2] contains a generator of 7 bytearrays, one per row (and each row is a day of the week)
    values = list(img[2])
    our_row = values[image_row]

    # Is the image wide enough?
    # Rem: our row holds 4 values per pixel
    if (image_column * 4 >= len(our_row)):
        return False

    # For now, assume an RGBA image, where any black dot signifies "write something" and ignore all else
    idx = image_column * 4
    is_black = our_row[idx] == our_row[idx+1] and our_row[idx+1] == our_row[idx+2] and our_row[idx] == 0

    return is_black


def test(image_filename):

    for day_in_week in range(7):

        # Github shows the calendar with Sunday at the top, as day 0
        # So let's start on the last Sunday of last year
        start_date = date(2024, 12, 29) + timedelta(days=day_in_week)
        end_date = date(2026, 1, 1)
        delta = timedelta(days=7)

        while start_date < end_date:
            print('.' if update_on_this_day(image_filename, start_date) else ' ', end='')
            start_date += delta

        print('')


def main():
    try:
        # Support ability to write messages in the log
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--filename')
        parser.add_argument('-t', '--test', action='store_true')
        pr = parser.parse_args()

        # For back compat, always update unless our visual checker tells us not
        update_number = True
        if pr.filename:
            test(pr.filename) if pr.test else None
            update_number = update_on_this_day(pr.filename, datetime.now())

        if update_number:
            current_number = read_number()
            new_number = current_number + 1
            write_number(new_number)

            git_commit()
            git_push()

        update_cron_with_random_time()

    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main() 