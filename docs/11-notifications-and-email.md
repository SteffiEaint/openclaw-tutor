# Notifications and Email Pipeline

## Purpose

The notification system converts educational progress information into actionable communication decisions.

## Inputs

The notification engine consumes:

- `reports/peppi_enriched_report.json`;
- `events/events.json`;
- Moodle student/course/enrollment data.

## Notification queue

The queue is stored in:

`reports/notification_queue.json`

Entries contain information such as:

- action;
- trigger;
- notification type;
- recipient type;
- recipient address;
- priority;
- student/course identifiers;
- progress percentage;
- teacher context.

## Typical notification types

The current data demonstrates categories such as:

- reminders;
- warnings;
- teacher summaries;
- event-related messages.

The exact decision logic should be treated as prototype logic and evaluated during testing rather than assumed to be a scientifically validated intervention model.

## Student email generation

`create_student_email.py` creates personalized student-facing email content based on progress information.

Typical content can include:

- student name;
- course;
- current progress;
- missing or overdue work;
- teacher/contact information;
- a course URL where available.

## Teacher email generation

`create_teacher_email.py` creates teacher-facing summaries so teachers can see which students may need attention.

## Aggregation

`generate_all_emails.py` coordinates generation and writes the result to `reports/generated_emails.json`.

## MailerMock integration

MailerMock reads generated email and presents it as a real-looking mailbox experience. This is useful because it lets a user demonstrate the complete communication loop without sending real email.

## Privacy and safety boundary

All development emails should remain inside the mock environment whenever possible. Real student data and real email addresses should not be introduced into the prototype merely to make the demo look more realistic.
