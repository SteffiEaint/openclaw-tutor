import json
from pathlib import Path

def load_json(filename):
    """
    Loads and parses a JSON file from the mocks/moodlemock/ directory.

    Args:
        filename (str): The name of the JSON file (e.g., "data.json").

    Returns:
        dict or list: The parsed JSON object.
    """
    # Construct the full path to the JSON file
    # Assumes the script is run from the openclaw-tutor root or similar context
    # where 'mocks/moodlemock/' is a relative path.
    file_path = Path("mocks/moodlemock/") / filename

    # Open the JSON file in read mode
    with open(file_path, 'r', encoding='utf-8') as f:
        # Load and parse the JSON content
        data = json.load(f)

    # Return the parsed JSON object
    return data


def count_completed_assignments(completions_data, student_ids=None):
    """
    Counts how many "completed" assignment records each student has.

    Args:
        completions_data (list): List of completion record dicts, each
            expected to have "studentId" and "status" keys.
        student_ids (iterable, optional): Full collection of student IDs to
            include in the result. Students with zero completed assignments
            will appear in the result with a count of 0. If omitted, only
            students who appear somewhere in completions_data (regardless of
            status) will be included, and only those with at least one
            "completed" record will show a non-zero count -- students with
            zero completed records but who DO appear in completions_data
            (e.g. with a "late" or "missing" status) will still show 0.

    Returns:
        dict: Mapping of studentId -> count of completed assignments,
            including entries with a count of 0.
    """
    student_completed_assignments = {}

    # Seed every known student with a count of 0 so students with no
    # completed assignments still show up in the result instead of being
    # silently dropped.
    if student_ids is not None:
        for student_id in student_ids:
            student_completed_assignments[student_id] = 0

    for completion in completions_data:
        # Get the studentId from the current completion record
        student_id = completion.get("studentId")

        if not student_id:
            continue

        # Make sure this student has an entry even if none of their
        # records are "completed" (e.g. all "late"/"missing"/"in-progress").
        student_completed_assignments.setdefault(student_id, 0)

        # Increment the count only when the assignment status is "completed"
        if completion.get("status") == "completed":
            student_completed_assignments[student_id] += 1

    return student_completed_assignments


if __name__ == "__main__":
    # Load specific JSON files
    students_data = load_json("students.json")
    courses_data = load_json("courses.json")
    assignments_data = load_json("assignments.json")
    enrollments_data = load_json("enrollments.json")
    completions_data = load_json("assignmentCompletions.json")

    print(type(completions_data), len(completions_data))
    print(completions_data[0])

    student_completed_assignments = count_completed_assignments(
        completions_data,
        student_ids=[s["studentId"] for s in students_data],
    )
    print(student_completed_assignments)