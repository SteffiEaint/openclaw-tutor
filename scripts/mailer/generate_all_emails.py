import json
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

    student_emails = []
    teacher_summary_emails = []

    for notification in notifications:
        recipient_type = notification.get("recipient_type")
        notification_type = notification.get("notification_type")

        if recipient_type == "student":
            student_emails.append(
                generate_student_email_object(notification)
            )

        elif (
            recipient_type == "teacher"
            and notification_type == "teacher_summary"
        ):

            teacher_summary_emails.append(
                generate_teacher_summary_email_object(
                    notification
                )
            )

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