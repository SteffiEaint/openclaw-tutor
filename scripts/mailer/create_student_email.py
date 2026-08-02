import json
from pathlib import Path

def generate_student_email_object(notification):

    student_name = notification.get("student_name", "Student")
    student_email = notification.get("recipient")
    course_name = notification.get("course_name", "your course")
    progress = notification.get("progress_percentage")
    notification_type = notification.get("notification_type")

    # Subject
    if notification_type == "warning":
        subject = f"Action Required: {course_name}"

    elif notification_type == "reminder":
        subject = f"Reminder: {course_name}"

    elif notification_type == "encouragement":
        subject = f"Keep Going in {course_name}"

    elif notification_type == "motivation":
        subject = f"Great Progress in {course_name}"

    elif notification_type == "congratulations":
        subject = f"Congratulations on Completing {course_name}"

    else:
        subject = f"Update for {course_name}"

    # Body
    body = f"Dear {student_name},\n\n"

    if notification_type == "warning":
        body += (
            f"Our records show that you currently have "
            f"{progress}% progress in {course_name}.\n\n"
            "Please begin working on your assignments as soon as possible "
            "to avoid falling behind."
        )

    elif notification_type == "reminder":
        body += (
            f"You currently have {progress}% progress in "
            f"{course_name}.\n\n"
            "Please remember to complete your remaining assignments."
        )

    elif notification_type == "encouragement":
        body += (
            f"Great work! You currently have "
            f"{progress}% progress in {course_name}.\n\n"
            "Keep up the good work."
        )

    elif notification_type == "motivation":
        body += (
            f"You currently have {progress}% progress in "
            f"{course_name}.\n\n"
            "You're almost there! Keep going."
        )

    elif notification_type == "congratulations":
        body += (
            f"Congratulations!\n\n"
            f"You have successfully completed "
            f"{course_name} with {progress}% progress."
        )

    else:
        body += (
            f"This is an update regarding "
            f"{course_name}."
        )

    body += "\n\nBest regards,\nOpenClaw Tutor"

    return {
        "to": student_email,
        "subject": subject,
        "body": body,
        "type": "student_notification"
    }