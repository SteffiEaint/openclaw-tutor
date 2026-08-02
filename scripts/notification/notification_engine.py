import json
from pathlib import Path
from datetime import datetime

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Input / Output paths
ENRICHED_REPORT_PATH = BASE_DIR / "reports" / "peppi_enriched_report.json"
NOTIFICATION_QUEUE_PATH = BASE_DIR / "reports" / "notification_queue.json"

NOTIFICATION_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_ACTION = "send_email"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_notification(
    action,
    trigger,
    notification_type,
    recipient_type,
    recipient,
    student_data,
    priority
):
    return {
        "action": action,
        "trigger": trigger,
        "notification_type": notification_type,
        "recipient_type": recipient_type,
        "recipient": recipient,
        "priority": priority,
        "timestamp": datetime.now().isoformat(),

        "student_id": student_data.get("student_id"),
        "student_name": student_data.get("student_name"),
        "student_email": student_data.get("student_email"),

        "teacher_name": student_data.get("teacher_name"),
        "teacher_email": student_data.get("teacher_email"),

        "course_id": student_data.get("course_id"),
        "course_name": student_data.get("course_name"),
        "course_url": student_data.get("course_url"),

        "progress_percentage": student_data.get("progress_percentage")
    }


def create_notification_queue(trigger="scheduled"):

    try:
        enriched_report = load_json(ENRICHED_REPORT_PATH)

    except FileNotFoundError:
        print(f"Error: {ENRICHED_REPORT_PATH} not found.")
        return

    except json.JSONDecodeError:
        print(f"Error decoding {ENRICHED_REPORT_PATH}.")
        return

    notification_queue = []

    zero_progress_students_by_teacher = {}

    for student_data in enriched_report:

        student_id = student_data.get("student_id")
        student_email = student_data.get("student_email")
        course_name = student_data.get("course_name")
        progress_percentage = student_data.get("progress_percentage")

        teacher_email = student_data.get("teacher_email")
        teacher_name = student_data.get("teacher_name")

        if None in (
            student_id,
            student_email,
            course_name,
            progress_percentage
        ):
            print(f"Skipping incomplete record: {student_data}")
            continue

        notification_type = None
        priority = "low"

        if progress_percentage == 0:
            notification_type = "warning"
            priority = "high"

            if teacher_email and teacher_name:
                if teacher_email not in zero_progress_students_by_teacher:
                    zero_progress_students_by_teacher[teacher_email] = {
                        "teacher_name": teacher_name,
                        "students": []
                    }

                zero_progress_students_by_teacher[teacher_email]["students"].append({
                    "student_id": student_data.get("student_id"),
                    "student_name": student_data.get("student_name"),
                    "student_email": student_data.get("student_email"),
                    "course_id": student_data.get("course_id"),
                    "course_name": student_data.get("course_name"),
                    "course_url": student_data.get("course_url"),
                    "progress_percentage": student_data.get("progress_percentage")
                })

        elif progress_percentage <= 25:
            notification_type = "reminder"
            priority = "medium"

        elif progress_percentage <= 50:
            notification_type = "encouragement"
            priority = "medium"

        elif progress_percentage < 100:
            notification_type = "motivation"
            priority = "medium"

        elif progress_percentage == 100:
            notification_type = "congratulations"
            priority = "low"

        if notification_type:
            notification_queue.append(
                build_notification(
                    action=DEFAULT_ACTION,
                    trigger=trigger,
                    notification_type=notification_type,
                    recipient_type="student",
                    recipient=student_email,
                    student_data=student_data,
                    priority=priority
                )
            )

    # Teacher summary notifications
    for teacher_email, teacher_data in zero_progress_students_by_teacher.items():
        notification_queue.append({
            "action": DEFAULT_ACTION,
            "trigger": trigger,
            "notification_type": "teacher_summary",
            "recipient_type": "teacher",
            "recipient": teacher_email,
            "priority": "high",
            "timestamp": datetime.now().isoformat(),
            "teacher_name": teacher_data["teacher_name"],
            "teacher_email": teacher_email,
            "students": teacher_data["students"]
        })

    with open(
        NOTIFICATION_QUEUE_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(notification_queue, f, indent=4)

    print(
        f"Generated {len(notification_queue)} notifications."
    )

    print(
        f"Saved to {NOTIFICATION_QUEUE_PATH}"
    )


if __name__ == "__main__":
    create_notification_queue()