# Architecture and Data Flow

## High-level architecture

```text
                    ┌────────────────────┐
                    │   OpenClaw / AI    │
                    │ Agent & Workflows  │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │ Scheduler /        │
                    │ Trigger Manager    │
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌────────────────────┐
                    │    MoodleMock      │
                    │ students/courses/  │
                    │ assignments/       │
                    │ completions        │
                    └─────────┬──────────┘
                              │
                              ▼
                 student_progress_report.json
                              │
                              ▼
                    ┌────────────────────┐
                    │    PeppiMock       │
                    │ identity + study   │
                    │ context + teachers │
                    └─────────┬──────────┘
                              │
                              ▼
                   peppi_enriched_report.json
                              │
                              ▼
                    ┌────────────────────┐
                    │ Notification       │
                    │ Engine             │
                    └─────────┬──────────┘
                              │
                              ▼
                    notification_queue.json
                              │
                              ▼
                    ┌────────────────────┐
                    │ Mail generation    │
                    │ student/teacher    │
                    │ email templates    │
                    └─────────┬──────────┘
                              │
                              ▼
                    generated_emails.json
                              │
                              ▼
                    ┌────────────────────┐
                    │    MailerMock      │
                    │ inbox / sent /     │
                    │ compose / reply    │
                    └────────────────────┘
```

## Data ownership

### MoodleMock

Owns learning activity data:

- students;
- courses;
- enrollments;
- assignments;
- assignment completion records.

Teacher relationships are represented by `teacherId` in course records, with teacher identity information supplied by PeppiMock's teacher dataset.

### PeppiMock

Provides simulated institutional/person context:

- student profiles;
- teacher profiles;
- study rights/enrollment context where present;
- course URLs and related course metadata.

The enrichment script combines Moodle progress with Peppi information.

### MailerMock

Owns mock email messages and mailbox behavior. It derives valid student/teacher accounts from the mock identity data and imports generated OpenClaw email into recipient inboxes.

## Main workflow

1. MoodleMock data is loaded.
2. `generate_student_progress_report.py` calculates per-student, per-course progress.
3. `enrich_with_peppi.py` adds names, emails, teacher information, and course URLs.
4. `event_engine.py` detects changes and creates events such as new assignments, missing assignments, and completed assignments.
5. `notification_engine.py` turns relevant conditions into notification queue entries.
6. Mail generation scripts create student and teacher email content.
7. MailerMock exposes generated messages through user inboxes.
8. A human can inspect the result through the mock UIs.

## Why mocks are used

Using mocks avoids requiring access to real educational systems during development. This reduces privacy, access-control, and infrastructure dependencies while still allowing realistic end-to-end demonstrations.
