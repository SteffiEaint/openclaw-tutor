# OpenClaw Tutor Documentation Index

This documentation set describes the current OpenClaw Tutor prototype, its mock services, automation workflow, testing strategy, development setup, and remaining project work.

## Documentation map

| Document | Purpose |
|---|---|
| `01-project-overview.md` | Project purpose, scope, actors, and prototype boundaries |
| `02-architecture-and-data-flow.md` | End-to-end architecture and data flow |
| `03-summer-work-plan.md` | Consolidated summer workload and current status |
| `04-development-setup.md` | Local installation and startup instructions |
| `05-mock-environments.md` | Relationship between MoodleMock, PeppiMock, and MailerMock |
| `06-moodlemock-guide.md` | MoodleMock roles, screens, APIs, and workflows |
| `07-peppimock-guide.md` | PeppiMock roles, data, APIs, and use cases |
| `08-mailermock-guide.md` | MailerMock accounts, inboxes, sending, and generated mail |
| `09-openclaw-workflows.md` | Workflow scripts, reports, and module ordering |
| `10-events-and-scheduling.md` | Event detection, snapshots, triggers, and scheduler |
| `11-notifications-and-email.md` | Notification queue and email generation pipeline |
| `12-testing-and-validation.md` | Automated tests and manual validation scenarios |
| `13-api-reference.md` | Mock-service HTTP API reference |
| `14-deployment-and-operations.md` | Running the prototype locally and preparing CSC deployment |
| `15-troubleshooting.md` | Common problems and practical recovery steps |
| `16-project-progress-log.md` | Suggested development log for documenting summer work |
| `17-blog-post-source-notes.md` | Non-technical material that can support the final blog post |

## Important distinction

This is a prototype/mock environment. The mock services intentionally simplify authentication and external integrations. Passwords are not intended to provide real security, and JSON files are used instead of production databases.

The documentation therefore describes both **what is currently implemented** and **what remains a future/experimental feature**. Items marked as future work should not be presented as completed functionality in the final report.
