import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ASSIGNMENTS_PATH = BASE_DIR / "mocks" / "moodlemock" / "assignments.json"
ENROLLMENTS_PATH = BASE_DIR / "mocks" / "moodlemock" / "enrollments.json"
COMPLETIONS_PATH = BASE_DIR / "mocks" / "moodlemock" / "assignmentCompletions.json"

ASSIGNMENT_SNAPSHOT_PATH = BASE_DIR / "events" / "assignment_snapshot.json"
COMPLETION_SNAPSHOT_PATH = BASE_DIR / "events" / "completion_snapshot.json"
EVENTS_PATH = BASE_DIR / "events" / "events.json"


def load_json(path):
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def now():
    return datetime.now(timezone.utc)


def parse_date(date_string):
    return datetime.fromisoformat(
        date_string.replace("Z", "+00:00")
    )


def detect_new_assignments(events):
    assignments = load_json(ASSIGNMENTS_PATH)
    snapshot = load_json(ASSIGNMENT_SNAPSHOT_PATH)

    previous_ids = {
        assignment["assignmentId"]
        for assignment in snapshot
    }

    for assignment in assignments:
        if assignment["assignmentId"] not in previous_ids:
            events.append({
                "event": "new_assignment",
                "timestamp": now().isoformat(),
                "assignmentId": assignment["assignmentId"],
                "courseId": assignment["courseId"],
                "title": assignment["title"],
                "dueDate": assignment["dueDate"]
            })

    save_json(ASSIGNMENT_SNAPSHOT_PATH, assignments)


def create_missing_completion_records(events):
    assignments = load_json(ASSIGNMENTS_PATH)
    enrollments = load_json(ENROLLMENTS_PATH)
    completions = load_json(COMPLETIONS_PATH)

    existing = {
        (completion["studentId"], completion["assignmentId"])
        for completion in completions
    }

    assignments_by_course = {}

    for assignment in assignments:
        assignments_by_course.setdefault(
            assignment["courseId"], []
        ).append(assignment)

    next_id = 1

    if completions:
        next_id = max(
            int(completion["completionId"].replace("CM", ""))
            for completion in completions
        ) + 1

    for enrollment in enrollments:
        student_id = enrollment["studentId"]
        course_id = enrollment["courseId"]

        for assignment in assignments_by_course.get(course_id, []):
            key = (student_id, assignment["assignmentId"])

            if key in existing:
                continue

            completions.append({
                "completionId": f"CM{next_id:03d}",
                "studentId": student_id,
                "assignmentId": assignment["assignmentId"],
                "status": "in-progress",
                "submittedAt": None
            })

            events.append({
                "event": "completion_created",
                "timestamp": now().isoformat(),
                "studentId": student_id,
                "assignmentId": assignment["assignmentId"],
                "courseId": course_id
            })

            existing.add(key)
            next_id += 1

    save_json(COMPLETIONS_PATH, completions)


def detect_due_dates(events):
    assignments = load_json(ASSIGNMENTS_PATH)
    completions = load_json(COMPLETIONS_PATH)

    assignment_lookup = {
        assignment["assignmentId"]: assignment
        for assignment in assignments
    }

    changed = False

    for completion in completions:
        if completion["status"] != "in-progress":
            continue

        assignment = assignment_lookup.get(
            completion["assignmentId"]
        )

        if assignment is None:
            continue

        due_date = parse_date(assignment["dueDate"])

        if now() > due_date:
            completion["status"] = "missing"
            changed = True

            events.append({
                "event": "assignment_missing",
                "timestamp": now().isoformat(),
                "studentId": completion["studentId"],
                "assignmentId": completion["assignmentId"]
            })

    if changed:
        save_json(COMPLETIONS_PATH, completions)


def detect_completed_assignments(events):
    completions = load_json(COMPLETIONS_PATH)
    snapshot = load_json(COMPLETION_SNAPSHOT_PATH)
    assignments = load_json(ASSIGNMENTS_PATH)

    previous = {
        completion["completionId"]: completion
        for completion in snapshot
    }

    assignment_lookup = {
        assignment["assignmentId"]: assignment
        for assignment in assignments
    }

    for completion in completions:
        old = previous.get(completion["completionId"])

        if old is None:
            continue

        if (
            old.get("status") != "completed"
            and completion.get("status") == "completed"
        ):
            events.append({
                "event": "assignment_completed",
                "timestamp": now().isoformat(),
                "studentId": completion["studentId"],
                "assignmentId": completion["assignmentId"]
            })

        if (
            completion.get("submittedAt")
            and old.get("submittedAt") != completion["submittedAt"]
        ):
            assignment = assignment_lookup.get(
                completion["assignmentId"]
            )

            if assignment is None:
                continue

            due = parse_date(assignment["dueDate"])
            submitted = parse_date(completion["submittedAt"])

            if submitted > due:
                completion["status"] = "late"

                events.append({
                    "event": "assignment_submitted_late",
                    "timestamp": now().isoformat(),
                    "studentId": completion["studentId"],
                    "assignmentId": completion["assignmentId"]
                })

    save_json(COMPLETION_SNAPSHOT_PATH, completions)
    save_json(COMPLETIONS_PATH, completions)


def main():
    events = []

    detect_new_assignments(events)
    create_missing_completion_records(events)
    detect_due_dates(events)
    detect_completed_assignments(events)

    save_json(EVENTS_PATH, events)

    print(f"Created {len(events)} events.")


if __name__ == "__main__":
    main()
