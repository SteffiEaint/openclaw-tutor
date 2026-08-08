import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENRICHED_REPORT_PATH = BASE_DIR / "reports" / "peppi_enriched_report.json"
EVENTS_PATH = BASE_DIR / "events" / "events.json"

STUDENTS_PATH = BASE_DIR / "mocks" / "moodlemock" / "students.json"
COURSES_PATH = BASE_DIR / "mocks" / "moodlemock" / "courses.json"
ENROLLMENTS_PATH = BASE_DIR / "mocks" / "moodlemock" / "enrollments.json"

NOTIFICATION_QUEUE_PATH = BASE_DIR / "reports" / "notification_queue.json"

DEFAULT_ACTION = "send_email"


def load_json(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def timestamp():
    return datetime.now().isoformat()


def build_notification(
    notification_type,
    recipient_type,
    recipient,
    priority,
    trigger,
    **fields
):
    notification = {
        "action": DEFAULT_ACTION,
        "trigger": trigger,
        "notification_type": notification_type,
        "recipient_type": recipient_type,
        "recipient": recipient,
        "priority": priority,
        "timestamp": timestamp()
    }

    notification.update(fields)
    return notification


def create_notification_queue(trigger="scheduled"):
    notification_queue = []

    enriched_report = load_json(ENRICHED_REPORT_PATH)

    zero_progress_students_by_teacher = {}

    # Scheduled progress notifications
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
                    "course_id": student_data.get("course_id"),
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
                    notification_type=notification_type,
                    recipient_type="student",
                    recipient=student_data.get("student_email"),
                    priority=priority,
                    trigger=trigger,
                    student_id=student_data.get("student_id"),
                    student_name=student_data.get("student_name"),
                    student_email=student_data.get("student_email"),
                    teacher_name=student_data.get("teacher_name"),
                    teacher_email=student_data.get("teacher_email"),
                    course_id=student_data.get("course_id"),
                    course_name=student_data.get("course_name"),
                    course_url=student_data.get("course_url"),
                    progress_percentage=progress
                )
            )

    # Teacher summaries
    for teacher_email, teacher_data in zero_progress_students_by_teacher.items():
        notification_queue.append(
            build_notification(
                notification_type="teacher_summary",
                recipient_type="teacher",
                recipient=teacher_email,
                priority="high",
                trigger=trigger,
                teacher_name=teacher_data["teacher_name"],
                teacher_email=teacher_email,
                students=teacher_data["students"]
            )
        )

    students = load_json(STUDENTS_PATH)
    courses = load_json(COURSES_PATH)
    enrollments = load_json(ENROLLMENTS_PATH)
    events = load_json(EVENTS_PATH)

    student_lookup = {
        student["studentId"]: student
        for student in students
    }

    course_lookup = {
        course["courseId"]: course
        for course in courses
    }

    def assignment_fields(event):
        assignment_id = event.get("assignmentId")
        assignment = next(
            (
                item
                for item in load_json(
                    BASE_DIR / "mocks" / "moodlemock" / "assignments.json"
                )
                if item.get("assignmentId") == assignment_id
            ),
            {}
        )

        course_id = event.get("courseId", assignment.get("courseId"))
        course = course_lookup.get(course_id, {})

        return {
            "assignment_id": assignment_id,
            "assignment_title": event.get("title", assignment.get("title")),
            "due_date": event.get("dueDate", assignment.get("dueDate")),
            "course_id": course_id,
            "course_name": course.get("courseName")
        }

    for event in events:
        event_type = event.get("event")

        if event_type == "new_assignment":
            fields = assignment_fields(event)

            for enrollment in enrollments:
                if enrollment["courseId"] != event["courseId"]:
                    continue

                student = student_lookup.get(enrollment["studentId"])

                if not student:
                    continue

                notification_queue.append(
                    build_notification(
                        notification_type="new_assignment",
                        recipient_type="student",
                        recipient=student["email"],
                        priority="medium",
                        trigger="event",
                        student_id=student["studentId"],
                        student_name=student["name"],
                        student_email=student["email"],
                        **fields
                    )
                )

        elif event_type in {
            "assignment_completed",
            "assignment_missing",
            "assignment_submitted_late"
        }:
            student = student_lookup.get(event.get("studentId"))

            if not student:
                continue

            fields = assignment_fields(event)

            priority = {
                "assignment_completed": "low",
                "assignment_submitted_late": "medium",
                "assignment_missing": "high"
            }[event_type]

            notification_queue.append(
                build_notification(
                    notification_type=event_type,
                    recipient_type="student",
                    recipient=student["email"],
                    priority=priority,
                    trigger="event",
                    student_id=student["studentId"],
                    student_name=student["name"],
                    student_email=student["email"],
                    **fields
                )
            )

    NOTIFICATION_QUEUE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

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
