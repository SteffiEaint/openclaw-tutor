# Summer Work Plan and Workload Documentation

This document consolidates the project workload developed during planning and connects it to the current prototype.

## Phase 1 — Architecture and risk reduction

### Weeks 1–2

Planned work:

- study OpenClaw architecture;
- verify Telegram integration;
- evaluate Gemini and Ollama;
- define Tutor System architecture;
- identify external dependencies;
- document risks;
- clarify Moodle, Peppi, LianaMailer, and CSC expectations.

Expected deliverables:

- architecture diagram;
- initial OpenClaw configuration;
- AI comparison table;
- risk register.

### Weeks 3–4

Planned work:

- design MoodleMock;
- design PeppiMock;
- design LianaMailerMock/MailerMock;
- define schemas;
- define tutoring workflows;
- create mock APIs and test datasets.

Expected deliverables:

- student/course/assignment schemas;
- mock APIs;
- test datasets.

## Phase 2 — Local prototype development

### Weeks 5–6

- build mock environments;
- connect OpenClaw workflows to mock data;
- demonstrate complete local scenarios.

### Week 7

- implement inactivity/0-activity detection;
- implement student lookup;
- implement assignment completion tracking;
- produce inactivity/progress reports.

### Week 8

- implement teacher reporting;
- implement student notifications;
- generate email content.

## Phase 3 — Automation and AI integration

### Week 9

- scheduled execution;
- trigger engine;
- confirmation/workflow execution.

### Week 10

- compare Ollama, Gemini, and alternative providers;
- document cost/performance trade-offs.

### Week 11

- refine WebUI/configuration experience;
- evaluate feasibility of deeper OpenClaw UI customization.

## Phase 4 — CSC deployment

### Week 12

- deploy prototype to CSC;
- configure resources and network access;
- validate remote execution.

### Week 13

- run end-to-end tests covering teacher requests, scheduled tasks, Telegram commands, email workflows, MoodleMock, and PeppiMock.

## Phase 5 — Documentation and publication

### Week 14

- technical documentation;
- user documentation;
- architecture documentation;
- AI comparison results;
- blog post updates;
- final report preparation.

## Workload note

The earlier detailed plan contained a total estimate of approximately 510 hours across 13 weeks, while the later risk-reduction plan reorganized the work into 14 phases/weeks. These plans should be treated as planning estimates rather than measured actual hours. The final report should replace estimates with actual logged hours where available.

## Current implementation status

The repository now contains substantial prototype implementation across:

- mock educational services;
- UI work;
- progress analysis;
- event detection;
- notification generation;
- email generation;
- scheduling;
- automated testing.

Remaining work should focus on integration validation, deployment, model comparison, documentation, screenshots/diagrams, and final evaluation rather than adding unnecessary production features.
