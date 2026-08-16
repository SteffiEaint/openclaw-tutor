#!/usr/bin/env python3
"""OpenClaw-facing Tutor System tool adapter.

This adapter deliberately reuses the existing project data and deterministic
Python workflow scripts. OpenClaw can call it through its built-in `exec` tool.
All command results are JSON so the agent can reason over them reliably.
"""

import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
REPORTS_DIR = BASE_DIR / "reports"
CONFIG_PATH = BASE_DIR / "config" / "tutor_config.json"
MOODLE_DIR = BASE_DIR / "mocks" / "moodlemock"
PEPPI_DIR = BASE_DIR / "mocks" / "peppimock"

WORKFLOW = BASE_DIR / "scheduler" / "workflow.py"


def load_json(path, default=None):
    if not path.exists():
        return [] if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [] if default is None else default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def result_ok(data=None, **extra):
    value = {"success": True}
    if data is not None:
        value["data"] = data
    value.update(extra)
    return value


def result_error(message):
    return {"success": False, "error": message}


def normalize(value):
    return str(value or "").strip().lower()


def find_course(course_id):
    courses = load_json(MOODLE_DIR / "courses.json", [])
    value = normalize(course_id)
    return next(
        (c for c in courses if normalize(c.get("courseId")) == value),
        None,
    )


def course_context(course_id):
    course = find_course(course_id)
    if not course:
        return None

    teachers = load_json(PEPPI_DIR / "teachers.json", [])
    urls = load_json(PEPPI_DIR / "course_urls.json", [])
    teacher = next(
        (t for t in teachers if normalize(t.get("teacher_id")) == normalize(course.get("teacherId"))),
        None,
    )
    url = next(
        (u for u in urls if normalize(u.get("course_id")) == normalize(course_id)),
        None,
    )

    return {
        "course": course,
        "teacher": teacher,
        "courseUrl": url.get("course_url") if url else None,
    }


def get_course(course_id):
    context = course_context(course_id)
    if not context:
        return result_error(f"Course not found: {course_id}")
    return result_ok(context)


def get_enrolled_students(course_id):
    context = course_context(course_id)
    if not context:
        return result_error(f"Course not found: {course_id}")

    enrollments = load_json(MOODLE_DIR / "enrollments.json", [])
    students = load_json(PEPPI_DIR / "students.json", [])
    student_map = {normalize(s.get("studentId")): s for s in students}

    enrolled = []
    for enrollment in enrollments:
        if normalize(enrollment.get("courseId")) != normalize(course_id):
            continue
        student = student_map.get(normalize(enrollment.get("studentId")))
        if not student:
            continue
        enrolled.append({
            "studentId": student.get("studentId"),
            "name": student.get("name"),
            "email": student.get("email"),
            "enrollmentId": enrollment.get("enrollmentId"),
        })

    return result_ok({
        "course": context["course"],
        "courseUrl": context["courseUrl"],
        "teacher": context["teacher"],
        "students": enrolled,
    })


def get_student_emails(course_id):
    enrolled = get_enrolled_students(course_id)
    if not enrolled["success"]:
        return enrolled
    return result_ok({
        "courseId": course_id,
        "students": [
            {
                "studentId": s["studentId"],
                "name": s["name"],
                "email": s["email"],
            }
            for s in enrolled["data"]["students"]
            if s.get("email")
        ],
    })


def get_teacher(course_id):
    context = course_context(course_id)
    if not context:
        return result_error(f"Course not found: {course_id}")
    teacher = context.get("teacher")
    if not teacher:
        return result_error(f"No teacher found for course: {course_id}")
    return result_ok({
        "course": context["course"],
        "courseUrl": context["courseUrl"],
        "teacher": teacher,
    })


def get_activity(course_id):
    context = course_context(course_id)
    if not context:
        return result_error(f"Course not found: {course_id}")

    assignments = load_json(MOODLE_DIR / "assignments.json", [])
    completions = load_json(MOODLE_DIR / "assignmentCompletions.json", [])
    enrollments = load_json(MOODLE_DIR / "enrollments.json", [])
    students = load_json(PEPPI_DIR / "students.json", [])

    course_assignments = [
        a for a in assignments
        if normalize(a.get("courseId")) == normalize(course_id)
        and not str(a.get("assignmentId", "")).startswith("ATEST")
    ]
    assignment_map = {a.get("assignmentId"): a for a in course_assignments}
    student_map = {s.get("studentId"): s for s in students}

    rows = []
    for enrollment in enrollments:
        if normalize(enrollment.get("courseId")) != normalize(course_id):
            continue
        sid = enrollment.get("studentId")
        student = student_map.get(sid)
        if not student:
            continue

        student_completions = [
            c for c in completions
            if c.get("studentId") == sid and c.get("assignmentId") in assignment_map
        ]
        completed = [c for c in student_completions if c.get("status") == "completed"]
        submitted_or_returned = [
            c for c in student_completions
            if c.get("submittedAt") or c.get("status") in {"completed", "late"}
        ]
        # A missing-only completion record is not student activity.
        # Activity means submitted/returned work or an in-progress/completed/late record.
        recorded_activity = any(
            c.get("submittedAt")
            or c.get("status") in {"completed", "late", "in-progress"}
            for c in student_completions
        )

        rows.append({
            "studentId": sid,
            "studentName": student.get("name"),
            "studentEmail": student.get("email"),
            "assignmentCount": len(course_assignments),
            "completionRecords": len(student_completions),
            "completedAssignments": len(completed),
            "submittedOrReturned": len(submitted_or_returned),
            "recordedActivity": recorded_activity,
            "progressPercentage": round(
                len(completed) / len(course_assignments) * 100, 2
            ) if course_assignments else 0,
            "statuses": [c.get("status") for c in student_completions],
        })

    return result_ok({
        "course": context["course"],
        "courseUrl": context["courseUrl"],
        "teacher": context["teacher"],
        "assignments": course_assignments,
        "students": rows,
    })


def find_zero_activity(course_id):
    activity = get_activity(course_id)
    if not activity["success"]:
        return activity

    zero = []
    for student in activity["data"]["students"]:
        # Strict definition used by the project requirement:
        # no completed assignments, no returned/submitted work and no
        # recorded Moodle activity.
        if (
            student["completedAssignments"] == 0
            and student["submittedOrReturned"] == 0
            and not student["recordedActivity"]
        ):
            zero.append(student)

    return result_ok({
        "course": activity["data"]["course"],
        "courseUrl": activity["data"]["courseUrl"],
        "teacher": activity["data"]["teacher"],
        "zeroActivityStudents": zero,
        "count": len(zero),
    })


def save_zero_activity(course_id):
    report = find_zero_activity(course_id)
    if not report["success"]:
        return report

    path = REPORTS_DIR / "zero_activity_reports.json"
    history = load_json(path, [])
    if not isinstance(history, list):
        history = []

    entry = {
        "reportId": f"ZR-{uuid.uuid4().hex[:10].upper()}",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "courseId": report["data"]["course"].get("courseId"),
        "courseName": report["data"]["course"].get("courseName"),
        "courseUrl": report["data"].get("courseUrl"),
        "teacher": report["data"].get("teacher"),
        "zeroActivityStudents": report["data"]["zeroActivityStudents"],
        "count": report["data"]["count"],
    }
    history.append(entry)
    save_json(path, history)
    return result_ok(entry, reportPath=str(path))


def list_zero_activity_reports(course_id=None):
    """Return persisted zero-activity reports without recalculating activity."""
    path = REPORTS_DIR / "zero_activity_reports.json"
    history = load_json(path, [])
    if not isinstance(history, list):
        history = []

    if course_id:
        wanted = normalize(course_id)
        history = [
            report for report in history
            if normalize(report.get("courseId")) == wanted
        ]

    return result_ok({
        "reportPath": str(path),
        "count": len(history),
        "reports": history,
    })


def read_report(filename):
    path = REPORTS_DIR / filename
    if not path.exists():
        return result_error(f"Report not found: {filename}")
    try:
        return result_ok(json.loads(path.read_text(encoding="utf-8")))
    except json.JSONDecodeError as exc:
        return result_error(f"Invalid JSON in {filename}: {exc}")


def run_workflow():
    result = subprocess.run(
        [sys.executable, str(WORKFLOW)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return result_error(result.stderr.strip() or result.stdout.strip())
    return result_ok(message="Tutor workflow completed successfully.", output=result.stdout)


def append_generated_email(category, email, prefix):
    path = REPORTS_DIR / "generated_emails.json"
    generated = load_json(path, {})
    if not isinstance(generated, dict):
        generated = {}
    generated.setdefault("student_emails", [])
    generated.setdefault("teacher_summary_emails", [])

    run_id = f"OC-{uuid.uuid4().hex[:12]}"
    email["emailId"] = f"{run_id}-{prefix}-{len(generated[category]) + 1:03d}"
    email["workflowRunId"] = run_id
    email["generatedAt"] = datetime.now(timezone.utc).isoformat()
    generated[category].append(email)
    save_json(path, generated)
    return email


def send_teacher_report(course_id):
    report = find_zero_activity(course_id)
    if not report["success"]:
        return report

    teacher = report["data"].get("teacher") or {}
    teacher_email = teacher.get("teacher_email")
    if not teacher_email:
        return result_error("The course has no teacher email in PeppiMock.")

    students = report["data"]["zeroActivityStudents"]
    body = [
        f"Dear {teacher.get('teacher_name', 'Teacher')},",
        "",
        f"Zero-activity report for {report['data']['course'].get('courseName')}.",
        "",
    ]
    if students:
        body.append("The following enrolled students currently have no recorded Moodle activity:")
        body.append("")
        for s in students:
            body.append(f"- {s.get('studentName')} ({s.get('studentEmail')})")
    else:
        body.append("No zero-activity students were found.")
    body.extend(["", "Best regards,", "OpenClaw Tutor"])

    email = append_generated_email(
        "teacher_summary_emails",
        {
            "to": teacher_email,
            "subject": f"Zero-Activity Report: {report['data']['course'].get('courseName')}",
            "body": "\n".join(body),
            "type": "teacher_summary",
        },
        "TEA",
    )

    return result_ok({
        "recipient": teacher_email,
        "courseId": course_id,
        "zeroActivityCount": len(students),
        "email": email,
    }, message="Teacher report generated for MailerMock.")


def send_student_warning(course_id):
    report = find_zero_activity(course_id)
    if not report["success"]:
        return report

    students = report["data"]["zeroActivityStudents"]
    course_name = report["data"]["course"].get("courseName", course_id)
    generated = []

    for student in students:
        email = student.get("studentEmail")
        if not email:
            continue
        generated.append(
            append_generated_email(
                "student_emails",
                {
                    "to": email,
                    "subject": f"Action Required: {course_name}",
                    "body": (
                        f"Dear {student.get('studentName', 'Student')},\n\n"
                        f"Our records show that you currently have no recorded activity in {course_name}.\n\n"
                        "Please begin working on the course as soon as possible. "
                        "Continued inactivity may result in removal from the class, according to course policy.\n\n"
                        "Best regards,\nOpenClaw Tutor"
                    ),
                    "type": "student_notification",
                    "deliveryMode": "bcc-simulated",
                },
                "STU",
            )
        )

    return result_ok({
        "courseId": course_id,
        "recipientCount": len(generated),
        "deliveryMode": "bcc-simulated via MailerMock mailbox delivery",
        "emails": generated,
    }, message="Student warnings generated for MailerMock.")


def config_get():
    return result_ok(load_json(CONFIG_PATH, {}))


def config_set(path, value):
    config = load_json(CONFIG_PATH, {})
    if not isinstance(config, dict):
        config = {}
    parts = path.split(".")
    cursor = config
    for part in parts[:-1]:
        if not isinstance(cursor.get(part), dict):
            cursor[part] = {}
        cursor = cursor[part]
    # JSON-friendly primitive values from CLI.
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value
    cursor[parts[-1]] = parsed
    save_json(CONFIG_PATH, config)
    return result_ok(config, message=f"Updated configuration key: {path}")


def dispatch(argv):
    if not argv:
        return result_error(
            "Missing command. Available: run_workflow, course, enrolled_students, "
            "student_emails, teacher, activity, zero_activity, save_zero_activity, "
            "teacher_report, student_warning, student_progress, peppi_data, "
            "notifications, emails, zero_activity_reports, config_get, config_set"
        )

    command = argv[0]
    if command == "run_workflow":
        return run_workflow()
    if command == "course" and len(argv) >= 2:
        return get_course(argv[1])
    if command == "enrolled_students" and len(argv) >= 2:
        return get_enrolled_students(argv[1])
    if command == "student_emails" and len(argv) >= 2:
        return get_student_emails(argv[1])
    if command == "teacher" and len(argv) >= 2:
        return get_teacher(argv[1])
    if command == "activity" and len(argv) >= 2:
        return get_activity(argv[1])
    if command == "zero_activity" and len(argv) >= 2:
        return find_zero_activity(argv[1])
    if command == "save_zero_activity" and len(argv) >= 2:
        return save_zero_activity(argv[1])
    if command == "teacher_report" and len(argv) >= 2:
        return send_teacher_report(argv[1])
    if command == "student_warning" and len(argv) >= 2:
        return send_student_warning(argv[1])
    if command == "student_progress":
        return read_report("student_progress_report.json")
    if command == "peppi_data":
        return read_report("peppi_enriched_report.json")
    if command == "notifications":
        return read_report("notification_queue.json")
    if command == "emails":
        return read_report("generated_emails.json")
    if command == "zero_activity_reports":
        return list_zero_activity_reports(argv[1] if len(argv) >= 2 else None)
    if command == "config_get":
        return config_get()
    if command == "config_set" and len(argv) >= 3:
        return config_set(argv[1], argv[2])
    return result_error(f"Invalid command or missing argument: {' '.join(argv)}")


def main():
    print(json.dumps(dispatch(sys.argv[1:]), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
