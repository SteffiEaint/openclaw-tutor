import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from create_student_email import generate_student_email_object
from create_teacher_email import generate_teacher_summary_email_object

BASE_DIR = Path(__file__).resolve().parent.parent.parent

NOTIFICATION_QUEUE_PATH = (
    BASE_DIR / "reports" / "notification_queue.json"
)

GENERATED_EMAILS_PATH = (
    BASE_DIR / "reports" / "generated_emails.json"
)


def generate_all_emails():
    try:
        with open(
            NOTIFICATION_QUEUE_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            notifications = json.load(f)

    except FileNotFoundError:
        print(f"{NOTIFICATION_QUEUE_PATH} not found.")
        return

    except json.JSONDecodeError:
        print("Invalid notification queue.")
        return

    run_id = f"RUN-{uuid.uuid4().hex[:12]}"
    generated_at = datetime.now(timezone.utc).isoformat()

    student_emails = []
    teacher_summary_emails = []

    for notification in notifications:
        recipient_type = notification.get("recipient_type")
        notification_type = notification.get("notification_type")

        if recipient_type == "student":
            email = generate_student_email_object(notification)
            email["emailId"] = f"{run_id}-STU-{len(student_emails)+1:03d}"
            email["workflowRunId"] = run_id
            email["generatedAt"] = generated_at
            student_emails.append(email)

        elif (
            recipient_type == "teacher"
            and notification_type == "teacher_summary"
        ):

            email = generate_teacher_summary_email_object(notification)
            email["emailId"] = f"{run_id}-TEA-{len(teacher_summary_emails)+1:03d}"
            email["workflowRunId"] = run_id
            email["generatedAt"] = generated_at
            teacher_summary_emails.append(email)

    output = {
        "student_emails": student_emails,
        "teacher_summary_emails": teacher_summary_emails
    }

    GENERATED_EMAILS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        GENERATED_EMAILS_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(output, f, indent=4)

    print(
        f"Generated {len(student_emails)} student emails"
    )

    print(
        f"Generated {len(teacher_summary_emails)} teacher emails"
    )

    print(
        f"Saved to {GENERATED_EMAILS_PATH}"
    )


if __name__ == "__main__":
    generate_all_emails()