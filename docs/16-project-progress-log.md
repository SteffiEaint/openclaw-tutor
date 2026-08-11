# Project Progress Log

Use this document as the running engineering diary for the summer project. Add dated entries after meaningful work rather than trying to reconstruct every detail at the end.

## Suggested entry format

### YYYY-MM-DD — Short title

**Work completed**

- What was implemented?
- Which files changed?
- Which workflow was affected?

**Testing**

- What was tested?
- Did automated tests pass?
- What screenshots or logs were captured?

**Problems**

- What failed?
- What caused it?

**Decision**

- What approach was chosen and why?

**Next step**

- What should happen next?

## Recommended milestones to record

### OpenClaw setup

Record installation, model-provider experiments, gateway/configuration issues, and lessons learned.

### Mock data design

Record how MoodleMock, PeppiMock, and MailerMock schemas were designed and why mock data was chosen.

### MoodleMock

Record student/teacher login, dashboards, assignment submission, course views, and event-related changes.

### PeppiMock

Record student/teacher/admin views and how course ownership/enrollment was connected to MoodleMock.

### MailerMock

Record inbox, sent mail, compose/reply, and generated-email ingestion.

### Event engine

Record how snapshot-based change detection was implemented and tested.

### Notification engine

Record notification types, priorities, and examples of useful/irrelevant alerts.

### AI model comparison

For every model/provider tested, record:

- model name;
- provider;
- local/cloud;
- task tested;
- response time;
- output quality;
- limitations;
- cost/free-tier behavior;
- hardware usage for local models.

### CSC deployment

Record environment configuration, resource limits, networking issues, and final deployment outcome.

### Final evaluation

Record which original project goals were achieved, partially achieved, or not achieved.
