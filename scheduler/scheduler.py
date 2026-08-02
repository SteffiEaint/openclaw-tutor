import json
import schedule
import time
from pathlib import Path

from workflow import run_full_workflow

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "tutor_config.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

scheduler = config["scheduler"]

if scheduler["mode"] == "daily":
    schedule.every().day.at(scheduler["time"]).do(run_full_workflow)

elif scheduler["mode"] == "interval":

    interval = scheduler["interval"]
    unit = scheduler["unit"]

    if unit == "seconds":
        schedule.every(interval).seconds.do(run_full_workflow)

    elif unit == "minutes":
        schedule.every(interval).minutes.do(run_full_workflow)

    elif unit == "hours":
        schedule.every(interval).hours.do(run_full_workflow)

print("Scheduler started.")

while True:
    schedule.run_pending()
    time.sleep(1)