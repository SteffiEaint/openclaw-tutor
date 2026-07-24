import json
from pathlib import Path

# Define file paths using pathlib for robust path handling
# Paths are relative to the script's location (openclaw-tutor/scripts/mailer/)
INPUT_REPORT_PATH = Path(__file__).resolve().parent.parent.parent / "reports" / "peppi_enriched_report.json"
OUTPUT_EMAILS_PATH = Path(__file__).resolve().parent.parent.parent / "reports" / "student_emails.json"

def generate_student_emails():
    """
    Reads the enriched student report and generates individual email objects
    for each inactive student.
    """
    # Load the enriched student report
    try:
        with open(INPUT_REPORT_PATH, 'r', encoding='utf-8') as f:
            students_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file not found at {INPUT_REPORT_PATH}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {INPUT_REPORT_PATH}")
        return

    # List to store the generated email objects for students
    student_emails = []

    # Iterate through each student in the report
    for student in students_data:
        student_email = student.get("student_email")
        student_name = student.get("student_name", "Student")
        course_name = student.get("course_name", "your course")
        course_url = student.get("course_url", "the course page")
        teacher_name = student.get("teacher_name", "Instructor")
        status = student.get("status", "0 activity")

        # Only generate an email if a valid student email is available
        if student_email:
            # Construct the email body
            email_body = (
                f"Dear {student_name},\n\n"
                f"This is a reminder regarding your activity in the course '{course_name}'. "
                f"Our records indicate {status}.\n\n"
                "To help you get back on track, please visit the course page here: "
                f"{course_url}\n\n"
                f"If you have any questions or need assistance, feel free to reach out to "
                f"your teacher, {teacher_name}.\n\n"
                "Best regards,\nYour OpenClaw Assistant"
            )

            # Create the email object
            email_object = {
                "to": student_email,
                "subject": "Course activity reminder",
                "body": email_body
            }
            student_emails.append(email_object)

    # Ensure the output directory exists
    OUTPUT_EMAILS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Save the generated email objects to a JSON file
    try:
        with open(OUTPUT_EMAILS_PATH, 'w', encoding='utf-8') as f:
            json.dump(student_emails, f, indent=4)
        print(f"Student emails successfully generated and saved to {OUTPUT_EMAILS_PATH}")
    except IOError as e:
        print(f"Error: Could not write output file to {OUTPUT_EMAILS_PATH}. {e}")

if __name__ == "__main__":
    generate_student_emails()
