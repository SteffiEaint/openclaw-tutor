import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENRICHED_REPORT_PATH = BASE_DIR / "reports" / "peppi_enriched_report.json"
EVENTS_PATH = BASE_DIR / "events" / "events.json"
STUDENTS_PATH = BASE_DIR / "mocks" / "moodlemock" / "students.json"
COURSES_PATH = BASE_DIR / "mocks" / "moodlemock" / "courses.json"
ENROLLMENTS_PATH = BASE_DIR / "mocks" / "moodlemock" / "enrollments.json"
NOTIFICATION_QUEUE_PATH = BASE_DIR / "reports" / "notification_queue.json"

NOTIFICATION_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)

DEFAULT_ACTION = "send_email"


def load_json(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_notification(
    action,
    trigger,
    notification_type,
    recipient_type,
    recipient,
    student_data,
    priority,
    extra=None
):
    notification = {
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

    if extra:
        notification.update(extra)

    return notification


def create_notification_queue(trigger="scheduled"):

    notification_queue = []

    # Scheduled Progress Notifications
    try:
        enriched_report = load_json(ENRICHED_REPORT_PATH)
    except Exception:
        enriched_report = []

    zero_progress_students_by_teacher = {}

    for student_data in enriched_report:
        progress = student_data.get("progress_percentage")

        if progress is None:
            continue

        notification_type = None
        priority = "low"

        if progress == 0:
            notification_type = "warning"
            priority = "high"

            teacher_email = student_data.get("teacher_email")
            teacher_name = student_data.get("teacher_name")

            if teacher_email:
                zero_progress_students_by_teacher.setdefault(
                    teacher_email,
                    {
                        "teacher_name": teacher_name,
                        "students": []
                    }
                )

                zero_progress_students_by_teacher[teacher_email]["students"].append({
                    "student_id": student_data.get("student_id"),
                    "student_name": student_data.get("student_name"),
                    "student_email": student_data.get("student_email"),
                    "course_name": student_data.get("course_name"),
                    "course_url": student_data.get("course_url"),
                    "progress_percentage": progress
                })

        elif progress <= 25:
            notification_type = "reminder"
            priority = "medium"

        elif progress <= 50:
            notification_type = "encouragement"
            priority = "medium"

        elif progress < 100:
            notification_type = "motivation"
            priority = "medium"

        elif progress == 100:
            notification_type = "congratulations"

        if notification_type:
            notification_queue.append(
                build_notification(
                    DEFAULT_ACTION,
                    trigger,
                    notification_type,
                    "student",
                    student_data.get("student_email"),
                    student_data,
                    priority
                )
            )

    # Teacher summaries
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

    # Event-based Notifications
    events = load_json(EVENTS_PATH)
    students = load_json(STUDENTS_PATH)
    courses = load_json(COURSES_PATH)
    enrollments = load_json(ENROLLMENTS_PATH)

    student_lookup = {
        student["studentId"]: student
        for student in students
    }

    course_lookup = {
        course["courseId"]: course
        for course in courses
    }

    for event in events:
        # New Assignment
        if event["event"] == "new_assignment":
            course = course_lookup.get(event["courseId"], {})
            course_name = course.get("courseName", "Unknown Course")

            for enrollment in enrollments:
                if enrollment["courseId"] != event["courseId"]:
                    continue

                student = student_lookup.get(enrollment["studentId"])

                if not student:
                    continue

                notification_queue.append({
                    "action": DEFAULT_ACTION,
                    "trigger": "event",
                    "notification_type": "new_assignment",
                    "recipient_type": "student",
                    "recipient": student["email"],
                    "priority": "medium",
                    "timestamp": datetime.now().isoformat(),
                    "student_id": student["studentId"],
                    "student_name": student["name"],
                    "student_email": student["email"],
                    "course_id": event["courseId"],
                    "course_name": course_name,
                    "assignmentId": event["assignmentId"],
                    "title": event["title"],
                    "dueDate": event["dueDate"]
                })

        # Assignment Completed
        elif event["event"] == "assignment_completed":
            student = student_lookup.get(event["studentId"])
            if student:
                notification_queue.append({
                    "action": DEFAULT_ACTION,
                    "trigger": "event",
                    "notification_type": "assignment_completed",
                    "recipient_type": "student",
                    "recipient": student["email"],
                    "priority": "low",
                    "timestamp": datetime.now().isoformat(),
                    "student_id": student["studentId"],
                    "student_name": student["studentName"],
                    "student_email": student["email"],
                    **event
                })

        # Assignment Missing
        elif event["event"] == "assignment_missing":
            student = student_lookup.get(event["studentId"])
            if student:
                notification_queue.append({
                    "action": DEFAULT_ACTION,
                    "trigger": "event",
                    "notification_type": "assignment_missing",
                    "recipient_type": "student",
                    "recipient": student["email"],
                    "priority": "high",
                    "timestamp": datetime.now().isoformat(),
                    "student_id": student["studentId"],
                    "student_name": student["studentName"],
                    "student_email": student["email"],
                    **event
                })

    # Save queue
    with open(
        NOTIFICATION_QUEUE_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(notification_queue, f, indent=4)

    print(f"Generated {len(notification_queue)} notifications.")
    print(f"Saved to {NOTIFICATION_QUEUE_PATH}")

if __name__ == "__main__":
    create_notification_queue()