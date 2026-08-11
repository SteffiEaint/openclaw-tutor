# OpenClaw Workflow Guide

## Workflow entry point

The main local workflow is `scheduler/workflow.py`.

It reads `config/tutor_config.json` and executes enabled modules in sequence.

## Module sequence

### 1. Moodle progress report

`generate_student_progress_report.py` reads MoodleMock data and produces:

`reports/student_progress_report.json`

The report contains per-student, per-course information such as:

- completed assignments;
- total assignments;
- progress percentage;
- last activity date;
- overdue assignments;
- derived status.

### 2. Peppi enrichment

`enrich_with_peppi.py` reads the Moodle report and adds institutional context.

Output:

`reports/peppi_enriched_report.json`

### 3. Event engine

`event_engine.py` detects changes in assignment and completion state and writes events to `events/events.json`.

### 4. Notification engine

`notification_engine.py` uses the enriched report and events to build a notification queue.

Output:

`reports/notification_queue.json`

### 5. Email generation

The mailer scripts generate student and teacher email content.

Output:

`reports/generated_emails.json`

### 6. Optional SMTP sending

If `dry_run` is disabled, the workflow can invoke the SMTP sender. For development, MailerMock is the safer demonstration path because it keeps messages local.

## Configuration

Example current configuration:

```json
{
  "modules": {
    "moodle": true,
    "peppi": true,
    "events": true,
    "notifications": true,
    "mailer": true
  },
  "dry_run": false,
  "scheduler": {
    "mode": "interval",
    "interval": 30,
    "unit": "seconds"
  }
}
```

Before running a long-lived scheduler, review `dry_run` and SMTP settings carefully.

## OpenClaw role

The repository's scripts provide deterministic local workflow steps. OpenClaw can act as the agent/orchestration layer around these tools, but the deterministic Python scripts should remain understandable and testable independently.

This separation is useful for the final project because it demonstrates which parts are ordinary software automation and which parts benefit from AI-agent reasoning.
