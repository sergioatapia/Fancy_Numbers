
## Setup

1. Clone this repository:

```bash
git clone https://github.com/teddyhabtamu/daily_task.git
cd daily_task
```

2. Run the script:

```bash
python update_number.py
```

3. Setup a cron job to run the script daily:

```bash
crontab -e
```

Add the following line to the crontab file:

```bash
0 6 * * * cd /path/to/your/repo && python update_number.py
```

This will run the script at 6am every day.

## Usage

The script will increment the number in `number.txt` and commit the change to git. You can modify the script to increment by any value or use a different file to store the number.

By running this you will be able get a fancy streak on your github profile and get a job.

![How to get a job](get_a_job.jpg)
