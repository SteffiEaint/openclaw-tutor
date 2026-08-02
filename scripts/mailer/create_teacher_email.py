def generate_teacher_summary_email_object(notification):

    teacher_email = notification.get("recipient")
    teacher_name = notification.get("teacher_name", "Teacher")
    students = notification.get("students", [])

    subject = "Summary: Students with 0% Progress"
    body = f"Dear {teacher_name},\n\n"

    body += (
        "The following students currently have "
        "0% progress:\n\n"
    )

    for student in students:

        body += (
            f"- {student.get('student_name')} "
            f"({student.get('student_email')})\n"
            f"  Course: {student.get('course_name')}\n"
            f"  Progress: "
            f"{student.get('progress_percentage')}%\n\n"
        )

    body += (
        "Please follow up with these students "
        "if necessary.\n\n"
        "Best regards,\n"
        "OpenClaw Tutor"
    )

    return {
        "to": teacher_email,
        "subject": subject,
        "body": body,
        "type": "teacher_summary"
    }