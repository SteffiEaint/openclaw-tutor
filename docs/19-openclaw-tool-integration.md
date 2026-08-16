# OpenClaw Tool Integration

## Purpose

This project uses OpenClaw as the orchestration/agent layer while keeping the existing Python workflow deterministic and independently testable.

OpenClaw Skills are instruction files that teach the agent how to use available capabilities. The `tutor-system` skill therefore uses OpenClaw's built-in `exec` capability to call small repository adapters. The adapters reuse the project's existing mock data and workflow scripts instead of introducing a second implementation.

## Entry point

The main adapter is:

```text
skills/tutor-system/scripts/tutor_tool.py
```

Thin command-specific entrypoints are in:

```text
skills/tutor-system/tools/
```

## Focused tools

```text
peppi_get_course.py
peppi_get_enrolled_students.py
peppi_get_student_emails.py
peppi_get_course_teacher.py
moodle_get_activity.py
find_zero_activity.py
save_zero_activity_report.py
view_zero_activity_reports.py
mailer_send_teacher_report.py
mailer_send_student_warning.py
run_full_workflow.py
```

All tools return JSON and use the repository root as their working directory.

## Example commands

```bash
python3 skills/tutor-system/tools/peppi_get_course.py C101
python3 skills/tutor-system/tools/peppi_get_enrolled_students.py C101
python3 skills/tutor-system/tools/moodle_get_activity.py C101
python3 skills/tutor-system/tools/find_zero_activity.py C101
python3 skills/tutor-system/tools/save_zero_activity_report.py C101
python3 skills/tutor-system/tools/view_zero_activity_reports.py C101
python3 skills/tutor-system/tools/mailer_send_teacher_report.py C101
```

## Persistent reports

Zero-activity reports are appended to:

```text
reports/zero_activity_reports.json
```

This is intentionally append-only at the application level so earlier reports are retained.

Persisted zero-activity reports can be viewed without rerunning the workflow with `view_zero_activity_reports.py` or the central adapter command `zero_activity_reports`.

Generated OpenClaw emails are appended to the existing `reports/generated_emails.json` arrays by the focused notification tools. MailerMock imports those messages into its mailbox store when `/api/data` is requested.

## OpenClaw loading

The skill lives at:

```text
skills/tutor-system/SKILL.md
```

Workspace skills have high precedence in OpenClaw's skill loading order. After changing the skill, start a new OpenClaw session/turn so the updated instructions are loaded.

## What this demonstrates

The resulting architecture demonstrates an agent/orchestration layer calling deterministic project capabilities:

```text
OpenClaw agent
      |
      | built-in exec
      v
Tutor System skill
      |
      v
Repository tool adapters
      |
      +--> PeppiMock data
      +--> MoodleMock data
      +--> existing workflow scripts
      +--> persistent reports
      +--> MailerMock generated mailbox messages
```

This keeps the AI responsible for deciding *which* operation to perform and the Python layer responsible for deterministic data access, comparison, persistence and mock-mail delivery.
