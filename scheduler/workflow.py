import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "tutor_config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def run_script(script):
    print(f"\nRunning {script.name}")
    subprocess.run(["python", str(script)], check=True)


def run_full_workflow():

    config = load_config()
    modules = config["modules"]

    if modules["moodle"]:
        run_script(
            BASE_DIR /
            "scripts/moodle/generate_student_progress_report.py"
        )

    if modules["peppi"]:
        run_script(
            BASE_DIR /
            "scripts/peppi/enrich_with_peppi.py"
        )

    if modules["notifications"]:
        run_script(
            BASE_DIR /
            "scripts/notification/notification_engine.py"
        )

    if modules["mailer"]:

        run_script(
            BASE_DIR /
            "scripts/mailer/generate_all_emails.py"
        )

        if not config["dry_run"]:
            run_script(
                BASE_DIR /
                "scripts/mailer/smtp_sender.py"
            )
        else:
            print("Dry run enabled. Emails were generated only.")


if __name__ == "__main__":
    run_full_workflow()