import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MOODLE_REPORT = BASE_DIR / "reports" / "student_progress_report.json"
PEPPI_DIR = BASE_DIR / "mocks" / "peppimock"
MOODLE_DIR = BASE_DIR / "mocks" / "moodlemock"

REPORT_DIR = BASE_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

def load_json(path):
    """Loads a JSON file from the given path."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# Load data
student_progress_report = load_json(MOODLE_REPORT)
peppi_students = load_json(PEPPI_DIR / "students.json")
teachers = load_json(PEPPI_DIR / "teachers.json")
course_urls = load_json(PEPPI_DIR / "course_urls.json")
enrollments = load_json(MOODLE_DIR / "enrollments.json")
courses = load_json(MOODLE_DIR / "courses.json")

# Create lookup maps
student_peppi_map = {
    s["studentId"]: s for s in peppi_students
}

# Create a map for courses including teacher info
course_info_map = {}
for course in courses:
    course_id = course["courseId"]
    teacher_id = course["teacherId"]
    teacher_data = next((t for t in teachers if t["teacher_id"] == teacher_id), None)
    course_url_data = next((c for c in course_urls if c["course_id"] == course_id), None)
    
    course_info_map[course_id] = {
        "course_name": course["courseName"],
        "teacher_name": teacher_data["teacher_name"] if teacher_data else None,
        "teacher_email": teacher_data["teacher_email"] if teacher_data else None,
        "course_url": course_url_data["course_url"] if course_url_data else None
    }

# Map enrollments to students
enriched = []

for student_entry in student_progress_report:
    student_id = student_entry.get("student_id")
    course_id = student_entry.get("course_id")

    if not student_id or not course_id:
        continue

    peppi_data = student_peppi_map.get(student_id)
    course_data = course_info_map.get(course_id)

    if not peppi_data or not course_data:
        continue

    # Create a new dictionary to avoid modifying the original student_entry directly
    enriched_student_entry = student_entry.copy()
    enriched_student_entry["student_name"] = peppi_data.get("name") # Overwrite with name from Peppi mock data
    enriched_student_entry["student_email"] = peppi_data.get("email")
    enriched_student_entry["teacher_name"] = course_data.get("teacher_name")
    enriched_student_entry["teacher_email"] = course_data.get("teacher_email")
    enriched_student_entry["course_name"] = course_data.get("course_name")
    enriched_student_entry["course_url"] = course_data.get("course_url")
    
    enriched.append(enriched_student_entry)

output_file = REPORT_DIR / "peppi_enriched_report.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(enriched, f, indent=4)

print("Peppi enrichment complete")
print(f"Students enriched: {len(enriched)}")
print(f"Saved to: {output_file}")
