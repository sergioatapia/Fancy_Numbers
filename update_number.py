#!/usr/bin/env python3
import os
import random
import subprocess
from datetime import datetime
import sys

def p():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

def r():
    with open('number.txt', 'r') as f:
        return int(f.read().strip())

def w(n):
    with open('number.txt', 'w') as f:
        f.write(str(n))

def c():
    subprocess.run(['git', 'add', 'number.txt'])
    subprocess.run(['git', 'commit', '-m', f"Update {datetime.now().strftime('%Y%m%d')}"])

def push():
    subprocess.run(['git', 'push'], capture_output=True, text=True)

def cron():
    h, m = random.randint(0, 23), random.randint(0, 59)
    cmd = f"{m} {h} * * * cd {os.getcwd()} && python3 {os.path.basename(__file__)}\n"
    temp = "/tmp/cron_temp"
    os.system(f"crontab -l > {temp} 2>/dev/null || true")
    with open(temp, "r") as f:
        lines = [line for line in f if "update_number.py" not in line]
    with open(temp, "a") as f:
        f.write(cmd)
    os.system(f"crontab {temp}")
    os.remove(temp)

def main():
    p()
    try:
        w(r() + 1)
        c()
        push()
        cron()
    except Exception as e:
        sys.exit(1)

if __name__ == "__main__":
    main()
