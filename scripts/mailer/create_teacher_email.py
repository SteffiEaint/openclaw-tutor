import json
from pathlib import Path
from collections import defaultdict

# Define file paths using pathlib for robust path handling
# Paths are relative to the script's location (openclaw-tutor/scripts/mailer/)
INPUT_REPORT_PATH = Path(__file__).resolve().parent.parent.parent / "reports" / "peppi_enriched_report.json"
OUTPUT_EMAILS_PATH = Path(__file__).resolve().parent.parent.parent / "reports" / "teacher_emails.json"

def generate_teacher_emails():
    """
    Reads the enriched student report, groups inactive students by teacher email,
    and generates email objects for each teacher.
    """
    # Load the enriched student report
    try:
        with open(INPUT_REPORT_PATH, 'r') as f:
            students_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {INPUT_REPORT_PATH}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {INPUT_REPORT_PATH}")
        return

    # Dictionary to hold students grouped by teacher email
    # defaultdict simplifies adding students without checking if the key exists
    teachers_inactive_students = defaultdict(list)

    # Iterate through students and group inactive ones by teacher email
    for student in students_data:
        # Filter for inactive students (status "0 assignments completed")
        if student.get("status") == "0 assignments completed": # CORRECTED STATUS STRING
            teacher_email = student.get("teacher_email")
            # Only process students with a valid teacher email
            if teacher_email:
                teachers_inactive_students[teacher_email].append(student)

    # List to store the generated email objects
    teacher_emails = []

    # Generate an email object for each teacher
    for teacher_email, students in teachers_inactive_students.items():
        # Extract teacher name from the first student in the list for this teacher
        # This assumes that all students for a given teacher will have the same teacher_name
        # If not, a more robust lookup or aggregation strategy might be needed.
        teacher_name = None
        if students:
            # Find a student with a non-null teacher_name
            for s in students:
                if s.get("teacher_name"):
                    teacher_name = s.get("teacher_name")
                    break
            if not teacher_name: # Fallback if no student has teacher_name
                teacher_name = "Teacher" # Generic name if not found

        # Create a list of student details for the email body
        student_list_for_body = "\n".join([
            f"- {s.get('student_name', 'N/A')} ({s.get('student_id', 'N/A')}) in {s.get('course_id', 'N/A')}"
            for s in students
        ])

        # Construct the email body
        email_body = (
            f"Dear {teacher_name},\n\n"
            "This is an automated report to inform you about students in your courses "
            "who have recorded 0 activity.\n\n"
            "Please find the list of inactive students below:\n"
            f"{student_list_for_body}\n\n"
            "Kindly reach out to these students to encourage their participation.\n\n"
            "Best regards,\nYour OpenClaw Assistant"
        )

        # Create the email object
        email_object = {
            "to": teacher_email,
            "subject": "Students with 0 activity",
            "body": email_body,
            "students": [
                {
                    "student_id": s.get("student_id"),
                    "student_name": s.get("student_name"),
                    "student_email": s.get("student_email"),
                    "course_id": s.get("course_id")
                }
                for s in students
            ]
        }
        teacher_emails.append(email_object)

    # Ensure the output directory exists
    OUTPUT_EMAILS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save the generated email objects to a JSON file
    try:
        with open(OUTPUT_EMAILS_PATH, 'w') as f:
            json.dump(teacher_emails, f, indent=4)
        print(f"Teacher emails successfully generated and saved to {OUTPUT_EMAILS_PATH}")
    except IOError as e:
        print(f"Error: Could not write output file to {OUTPUT_EMAILS_PATH}. {e}")

if __name__ == "__main__":
    generate_teacher_emails()
