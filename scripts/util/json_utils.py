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


def count_completed_assignments(completions_data):
    """
    Counts how many "completed" assignment records each student has.

    Args:
        completions_data (list): List of completion record dicts, each
            expected to have "studentId" and "status" keys.

    Returns:
        dict: Mapping of studentId -> count of completed assignments.
    """
    student_completed_assignments = {}

    for completion in completions_data:
        # Get the studentId from the current completion record
        student_id = completion.get("studentId")

        # Check if the student_id exists and if the assignment status is "completed"
        if student_id and completion.get("status") == "completed":
            # Increment the count for the student_id. If the student_id is not yet in
            # the dictionary, set its initial count to 1. Otherwise, increment it.
            student_completed_assignments[student_id] = (
                student_completed_assignments.get(student_id, 0) + 1
            )

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

    student_completed_assignments = count_completed_assignments(completions_data)
    print(student_completed_assignments)