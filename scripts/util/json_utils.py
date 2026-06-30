addimport json
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

# Load specific JSON files
students_data = load_json("students.json")
courses_data = load_json("courses.json")
assignments_data = load_json("assignments.json")
enrollments_data = load_json("enrollments.json")
completions_data = load_json("completions.json")
