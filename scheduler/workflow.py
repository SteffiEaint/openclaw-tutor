import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "tutor_config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_script(script):
    print(f"\nRunning {script.name}")

    subprocess.run(
        [sys.executable, str(script)],
        cwd=BASE_DIR,
        check=True
    )


def run_full_workflow():
    config = load_config()
    modules = config["modules"]

    if modules.get("moodle", False):
        run_script(
            BASE_DIR / "scripts/moodle/generate_student_progress_report.py"
        )

    if modules.get("peppi", False):
        run_script(
            BASE_DIR / "scripts/peppi/enrich_with_peppi.py"
        )

    if modules.get("events", False):
        run_script(
            BASE_DIR / "scripts/events/event_engine.py"
        )

    if modules.get("notifications", False):
        run_script(
            BASE_DIR / "scripts/notification/notification_engine.py"
        )

    if modules.get("mailer", False):
        run_script(
            BASE_DIR / "scripts/mailer/generate_all_emails.py"
        )

        if config.get("dry_run", True):
            print("\nDry run enabled. Emails were generated only.")
        else:
            run_script(
                BASE_DIR / "scripts/mailer/smtp_sender.py"
            )


if __name__ == "__main__":
    run_full_workflow()
