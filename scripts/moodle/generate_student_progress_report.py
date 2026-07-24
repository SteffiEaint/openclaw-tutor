import json
from pathlib import Path
from datetime import datetime

# Define the base directory for relative paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define paths to mock data and output report
MOODLE_MOCK_DIR = BASE_DIR / "mocks" / "moodlemock"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True) # Ensure reports directory exists

def load_json(directory, filename):
    """Loads a JSON file from the specified directory."""
    file_path = directory / filename
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_student_progress_report():
    # Load all necessary data from moodlemock
    students_data = load_json(MOODLE_MOCK_DIR, "students.json")
    courses_data = load_json(MOODLE_MOCK_DIR, "courses.json")
    assignments_data = load_json(MOODLE_MOCK_DIR, "assignments.json")
    enrollments_data = load_json(MOODLE_MOCK_DIR, "enrollments.json")
    completions_data = load_json(MOODLE_MOCK_DIR, "assignmentCompletions.json")

    # Create lookup maps for efficient access
    students_map = {s['studentId']: s for s in students_data}
    courses_map = {c['courseId']: c for c in courses_data}
    assignments_map = {a['assignmentId']: a for a in assignments_data}

    # Group assignments by course
    course_assignments = {}
    for assignment in assignments_data:
        course_id = assignment['courseId']
        if course_id not in course_assignments:
            course_assignments[course_id] = []
        course_assignments[course_id].append(assignment)

    # Group completions by student and course
    student_course_completions = {}
    for completion in completions_data:
        student_id = completion['studentId']
        assignment_id = completion['assignmentId']
        
        # Get course_id from assignment
        assignment_info = assignments_map.get(assignment_id)
        if not assignment_info:
            continue # Skip if assignment not found

        course_id = assignment_info['courseId']

        if student_id not in student_course_completions:
            student_course_completions[student_id] = {}
        if course_id not in student_course_completions[student_id]:
            student_course_completions[student_id][course_id] = []
        student_course_completions[student_id][course_id].append(completion)

    student_progress_report = []

    # Iterate through each student and their enrollments to generate the report
    for enrollment in enrollments_data:
        student_id = enrollment['studentId']
        course_id = enrollment['courseId']

        student_info = students_map.get(student_id)
        course_info = courses_map.get(course_id)

        if not student_info or not course_info:
            continue # Skip if student or course info is missing

        course_name = course_info['courseName']
        
        # Get assignments for this course
        total_assignments_in_course = len(course_assignments.get(course_id, []))
        
        # Get completions for this student in this course
        completions_for_student_course = student_course_completions.get(student_id, {}).get(course_id, [])

        completed_assignments_count = sum(1 for c in completions_for_student_course if c['status'] == 'completed')
        
        progress_percentage = (completed_assignments_count / total_assignments_in_course * 100) if total_assignments_in_course > 0 else 0

        # Calculate last activity date
        last_activity_date = None
        valid_completions = [c for c in completions_for_student_course if c.get('submittedAt')]
        if valid_completions:
            latest_completion = max(valid_completions, key=lambda x: datetime.strptime(x['submittedAt'], '%Y-%m-%dT%H:%M:%SZ'))
            last_activity_date = latest_completion['submittedAt'].split('T')[0]
        
        # Calculate assignments due
        assignments_due = []
        current_date = datetime.now() # Assuming current date for "due" calculation
        for assignment in course_assignments.get(course_id, []):
            assignment_id = assignment['assignmentId']
            # Check if assignment is not completed by this student in this course
            is_completed = any(c['assignmentId'] == assignment_id and c['status'] == 'completed' for c in completions_for_student_course)
            
            if not is_completed:
                due_date_str = assignment.get('dueDate')
                if due_date_str:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M:%SZ')
                    if due_date < current_date:
                        assignments_due.append(assignment['title'])
        
        # Determine status
        status = "Active"
        if progress_percentage == 0 and completions_for_student_course:
            status = "No completed assignments"
        elif not completions_for_student_course and not assignments_due:
            status = "No activity"
        elif progress_percentage < 50 and len(assignments_due) > 0:
            status = "Behind schedule"
        elif progress_percentage == 100:
            status = "Completed"


        student_progress_report.append({
            "student_id": student_id,
            "course_id": course_id,
            "course_name": course_name,
            "completed_assignments": completed_assignments_count,
            "total_assignments": total_assignments_in_course,
            "progress_percentage": round(progress_percentage, 2),
            "last_activity_date": last_activity_date,
            "assignments_due": assignments_due,
            "status": status
        })

    # Save the generated report
    output_file_path = REPORTS_DIR / "student_progress_report.json"
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(student_progress_report, f, indent=4)

    print(f"Generated student progress report and saved to {output_file_path}")
    print(f"Total entries in report: {len(student_progress_report)}")

if __name__ == "__main__":
    generate_student_progress_report()
