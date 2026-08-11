# OpenClaw Tutor

A prototype AI tutoring assistant project that connects mock educational data, progress analysis, event detection, notifications, email generation, and local mock user interfaces.

## Start here

Read [`docs/00-documentation-index.md`](docs/00-documentation-index.md) for the full documentation map.

## Core workflow

```text
MoodleMock
   ↓
Student progress report
   ↓
Peppi enrichment
   ↓
Event detection / notification decisions
   ↓
Email generation
   ↓
MailerMock
```

## Main services

- **MoodleMock** — learning activity, courses, assignments, completions, students, and teachers.
- **PeppiMock** — student/teacher institutional context and course relationships.
- **MailerMock** — local inbox, sent mail, compose/reply, and generated email delivery.

## Useful documents

- [Project overview](docs/01-project-overview.md)
- [Architecture and data flow](docs/02-architecture-and-data-flow.md)
- [Summer work plan](docs/03-summer-work-plan.md)
- [Development setup](docs/04-development-setup.md)
- [Mock environment guide](docs/05-mock-environments.md)
- [Workflow guide](docs/09-openclaw-workflows.md)
- [Testing guide](docs/12-testing-and-validation.md)
- [API reference](docs/13-api-reference.md)
- [Troubleshooting](docs/15-troubleshooting.md)
- [Blog source notes](docs/17-blog-post-source-notes.md)

## Prototype boundary

This is a development and demonstration environment. Authentication, authorization, storage, and external integrations are intentionally simplified. Do not use the mock credentials or services as production security mechanisms.
