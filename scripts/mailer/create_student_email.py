def generate_student_email_object(notification):
    student_name = notification.get("student_name", "Student")
    student_email = notification.get("recipient")
    course_name = notification.get("course_name", "your course")
    progress = notification.get("progress_percentage")
    notification_type = notification.get("notification_type")

    assignment_title = notification.get(
        "assignment_title",
        "an assignment"
    )
    due_date = notification.get(
        "due_date",
        "the due date"
    )

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
    elif notification_type == "new_assignment":
        subject = f"New Assignment in {course_name}"
    elif notification_type == "assignment_completed":
        subject = f"Assignment Completed: {assignment_title}"
    elif notification_type == "assignment_missing":
        subject = f"Assignment Missing: {assignment_title}"
    elif notification_type == "assignment_submitted_late":
        subject = f"Late Submission: {assignment_title}"
    else:
        subject = f"Update for {course_name}"

    body = f"Dear {student_name},\n\n"

    if notification_type == "warning":
        body += (
            f"Our records show that your current progress in "
            f"{course_name} is {progress}%.\n\n"
            "Please begin working on your coursework as soon as possible "
            "to avoid falling behind."
        )

    elif notification_type == "reminder":
        body += (
            f"You currently have {progress}% progress in "
            f"{course_name}.\n\n"
            "This is a friendly reminder to continue working on your "
            "remaining assignments."
        )

    elif notification_type == "encouragement":
        body += (
            f"Great work! You have reached {progress}% progress in "
            f"{course_name}.\n\n"
            "Keep up the good work!"
        )

    elif notification_type == "motivation":
        body += (
            f"You currently have {progress}% progress in "
            f"{course_name}.\n\n"
            "You're getting close to completing the course. Keep going!"
        )

    elif notification_type == "congratulations":
        body += (
            "Congratulations!\n\n"
            f"You have successfully completed {course_name} "
            f"with {progress}% progress.\n\n"
            "We hope you enjoyed the course and wish you all the best "
            "in your future studies."
        )

    elif notification_type == "new_assignment":
        body += (
            f"A new assignment has been published for {course_name}.\n\n"
            f"Assignment: {assignment_title}\n"
            f"Due date: {due_date}\n\n"
            "Please remember to complete it before the deadline."
        )

    elif notification_type == "assignment_completed":
        body += (
            f"Your submission for '{assignment_title}' "
            "has been successfully recorded.\n\n"
            "Thank you for submitting your work."
        )

    elif notification_type == "assignment_missing":
        body += (
            f"Our records show that the deadline for "
            f"'{assignment_title}' has passed and no submission was received.\n\n"
            "The assignment has now been marked as missing. "
            "Please contact your instructor if you believe this is incorrect."
        )

    elif notification_type == "assignment_submitted_late":
        body += (
            f"Your submission for '{assignment_title}' was received "
            "after the deadline.\n\n"
            "The submission has been marked as late."
        )

    else:
        body += f"This is an update regarding {course_name}."

    body += "\n\nBest regards,\nOpenClaw Tutor"

    return {
        "to": student_email,
        "subject": subject,
        "body": body,
        "type": "student_notification"
    }
