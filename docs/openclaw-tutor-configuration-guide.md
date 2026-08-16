# OpenClaw Tutor --- Setup and Configuration Guide

## 1. Purpose

This document describes the reproducible setup and configuration process for the OpenClaw Tutor prototype.

It is written so that another developer can reproduce the working configuration without needing access to the original setup history. The configuration values in this document were reconstructed from the current working OpenClaw configuration and the current `openclaw-tutor` project.

**Important:** this is a development/prototype environment. Do not copy real API keys, Telegram bot tokens, passwords, or OpenClaw gateway tokens into Git or into this document.

------------------------------------------------------------------------

# 2. System Overview

The project uses OpenClaw as the AI-agent/orchestration layer while the
repository's existing Python scripts perform deterministic data access,
analysis, persistence, and mock-mail operations.

``` text
                         ┌───────────────────────┐
                         │       OpenClaw         │
                         │                       │
                         │ Gemini / Ollama        │
                         │ Agent / Exec           │
                         │ Telegram               │
                         │ Scheduler / Cron       │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   Tutor System Skill  │
                         │       SKILL.md         │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Repository Tool       │
                         │ Adapters / Python     │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
        ┌───────────┐          ┌───────────┐          ┌────────────┐
        │ PeppiMock │          │ MoodleMock │          │ MailerMock │
        └───────────┘          └───────────┘          └────────────┘
              │                      │                      │
              └──────────────────────┼──────────────────────┘
                                     ▼
                         ┌───────────────────────┐
                         │ Persistent reports    │
                         │ and workflow state    │
                         └───────────────────────┘
```

The repository's normal deterministic workflow is:

``` text
Moodle progress report
        ↓
Peppi enrichment
        ↓
Event processing
        ↓
Notification generation
        ↓
Email generation
        ↓
MailerMock / SMTP mock
```

OpenClaw can use focused repository tools for on-demand tutoring tasks
while the existing scheduler/workflow remains independently executable.

------------------------------------------------------------------------

# 3. Prerequisites

Recommended environment:

-   Python 3.x
-   Node.js and npm
-   Git
-   Chrome/Chromium for browser testing
-   Ollama (optional, for local AI models)
-   Google Gemini API access (optional, for cloud-model testing)
-   Telegram bot (if Telegram integration is required)

The currently tested OpenClaw environment is:

``` text
OS: macOS
Architecture: arm64
Node.js: 22.22.1
OpenClaw: 2026.5.12
Gateway: local
Gateway port: 18789
Gateway authentication: token
Tailscale exposure: off
Primary model: google/gemini-2.5-flash
Workspace: ~/openclaw-tutor
```

Versions may differ on another machine. Use the currently supported
OpenClaw release unless reproducing the exact project environment is
required.

------------------------------------------------------------------------

# 4. Install OpenClaw

Install OpenClaw globally:

``` bash
npm install -g openclaw
```

Verify the installation:

``` bash
openclaw --version
```

Check the installation and runtime:

``` bash
openclaw status
```

A healthy local setup should report that the Gateway is reachable.

For additional diagnostics:

``` bash
openclaw doctor
```

If `openclaw doctor` proposes a configuration repair, review the proposed change before applying it.

------------------------------------------------------------------------

# 5. Initial OpenClaw Configuration

Start the configuration wizard:

``` bash
openclaw configure
```

For this project, the working configuration uses:

  Setting                  Value
  ------------------------ ------------------------
  Configuration mode       Local
  Gateway mode             Local
  Gateway bind             Loopback/local machine
  Gateway port             `18789`
  Gateway authentication   Token
  Tailscale exposure       Off

The Gateway should be available at:

``` text
http://127.0.0.1:18789/
```

Verify:

``` bash
openclaw status
```

The Gateway should show as reachable.

## Configuration file

OpenClaw stores its user-level configuration at:

``` text
~/.openclaw/openclaw.json
```

The exact location can be obtained with:

``` bash
openclaw config file
```

Do not copy the actual `openclaw.json` into public repositories because it may contain credentials and access tokens.

------------------------------------------------------------------------

# 6. Configure the Workspace

The Tutor System project is located at:

``` text
~/openclaw-tutor
```

The OpenClaw workspace should point to the project directory when configuring the agent.

The relevant project structure is:

``` text
openclaw-tutor/
├── config/
│   ├── tutor_config.json
│   └── triggers.json
├── docs/
├── events/
├── mocks/
│   ├── moodlemock/
│   ├── peppimock/
│   └── lianamailermock/
├── reports/
├── scheduler/
├── scripts/
├── skills/
│   └── tutor-system/
│       ├── SKILL.md
│       ├── scripts/
│       │   └── tutor_tool.py
│       └── tools/
├── tests/
└── ui/
    ├── moodlemock/
    ├── peppimock/
    └── mailermock/
```

The important OpenClaw skill file is:

``` text
skills/tutor-system/SKILL.md
```

------------------------------------------------------------------------

# 7. Configure the AI Model

## 7.1 Google Gemini

The current project configuration uses Google Gemini as the primary cloud model:

``` text
google/gemini-2.5-flash
```

Configure the Google provider through OpenClaw's configuration process:

``` bash
openclaw configure
```

Use your own Gemini API key.

Never document the real key. Use a placeholder such as:

``` text
<YOUR_GEMINI_API_KEY>
```

Verify the resulting model configuration:

``` bash
openclaw status
```

The active session should report the configured model.

## 7.2 Ollama

The project also has Ollama configured as an optional local-model provider.

Ollama normally runs at:

``` text
http://127.0.0.1:11434
```

Check installed models:

``` bash
ollama list
```

The current configuration includes models such as:

``` text
gemma4
llama3.1:8b
mistral:latest
qwen2.5:7b
llama3:latest
llama3.2:3b
```

It is not necessary to install every model. Install only the models required for the intended experiment.

The project uses Ollama to demonstrate that OpenClaw can use an internally running/local AI provider in addition to a cloud API.

------------------------------------------------------------------------

# 8. Configure Telegram

Telegram is enabled in the current OpenClaw configuration.

A new setup should:

1.  Create a Telegram bot using BotFather.
2.  Copy the bot token.
3.  Configure Telegram in OpenClaw.
4.  Keep the token private.
5.  Restart/reload OpenClaw if necessary.
6.  Verify the channel.

Use a placeholder in documentation:

``` text
<YOUR_TELEGRAM_BOT_TOKEN>
```

Verify:

``` bash
openclaw status
```

The expected state is similar to:

``` text
Telegram   ON   OK
```

The current configuration requires mentions in Telegram groups:

``` text
requireMention: true
```

This prevents the agent from responding to every group message.

------------------------------------------------------------------------

# 9. Install the Tutor System Project

Clone or copy the repository:

``` bash
git clone <REPOSITORY_URL>
cd openclaw-tutor
```

If the project is already present:

``` bash
cd ~/openclaw-tutor
```

Install root Node dependencies:

``` bash
npm install
```

The root package is primarily used for Playwright testing.

Each Vite UI has its own dependencies. If required:

``` bash
cd ui/moodlemock
npm install

cd ../peppimock
npm install

cd ../mailermock
npm install
```

Python dependencies should be installed according to the project's dependency files/environment.

------------------------------------------------------------------------

# 10. Start the Mock Services

The current local services use:

  Service        Port
  ------------ ------
  MoodleMock     8000
  PeppiMock      8001
  MailerMock     8002

Start each service in a separate terminal.

From the repository root:

``` bash
python3 mocks/moodlemock/server.py
```

``` bash
python3 mocks/peppimock/server.py
```

``` bash
python3 mocks/lianamailermock/server.py
```

The mock services provide the deterministic data used by the Tutor System.

------------------------------------------------------------------------

# 11. Start the Mock UIs

Each Vite UI is a separate frontend.

For MoodleMock:

``` bash
cd ~/openclaw-tutor/ui/moodlemock
npm run dev
```

For PeppiMock:

``` bash
cd ~/openclaw-tutor/ui/peppimock
npm run dev
```

For MailerMock:

``` bash
cd ~/openclaw-tutor/ui/mailermock
npm run dev
```

Vite prints the actual local URL and port when it starts.

------------------------------------------------------------------------

# 12. Configure the Tutor System

The repository's Tutor System configuration is stored in:

``` text
config/tutor_config.json
```

The current configuration enables:

``` json
{
  "modules": {
    "moodle": true,
    "peppi": true,
    "events": true,
    "notifications": true,
    "mailer": true
  }
}
```

The current scheduler configuration is:

``` json
{
  "scheduler": {
    "mode": "interval",
    "interval": 30,
    "unit": "seconds"
  }
}
```

The configuration also identifies the OpenClaw integration:

``` text
skill: tutor-system
toolEntrypoint: skills/tutor-system/scripts/tutor_tool.py
focusedToolsDir: skills/tutor-system/tools
```

## Important

Do not replace the entire configuration file when changing one value.

The OpenClaw Tutor skill provides:

``` bash
python3 skills/tutor-system/scripts/tutor_tool.py config_get
```

and:

``` bash
python3 skills/tutor-system/scripts/tutor_tool.py config_set <dot.path> <json-value>
```

For example:

``` bash
python3 skills/tutor-system/scripts/tutor_tool.py config_set modules.mailer true
```

------------------------------------------------------------------------

# 13. Configure the OpenClaw Tutor Skill

The skill is:

``` text
skills/tutor-system/SKILL.md
```

Its purpose is to tell the OpenClaw agent how to use the repository's existing deterministic capabilities.

The key design decision is:

> OpenClaw decides which operation to perform; the repository Python
> tools perform deterministic data access, comparison, persistence, and
> mock-service interaction.

This avoids duplicating the project's working Python logic inside OpenClaw.

After modifying `SKILL.md`, start a new OpenClaw session/turn so the updated skill instructions are loaded.

------------------------------------------------------------------------

# 14. Tutor System Tools

The current focused tools include:

``` text
peppi_get_course.py
peppi_get_enrolled_students.py
peppi_get_student_emails.py
peppi_get_course_teacher.py
moodle_get_activity.py
find_zero_activity.py
save_zero_activity_report.py
mailer_send_teacher_report.py
mailer_send_student_warning.py
run_full_workflow.py
```

They can be called directly from the repository root.

Examples:

``` bash
python3 skills/tutor-system/tools/peppi_get_course.py C101
```

``` bash
python3 skills/tutor-system/tools/peppi_get_enrolled_students.py C101
```

``` bash
python3 skills/tutor-system/tools/moodle_get_activity.py C101
```

``` bash
python3 skills/tutor-system/tools/find_zero_activity.py C101
```

The tools return JSON and use the repository root as their working directory.

------------------------------------------------------------------------

# 15. OpenClaw Tool Orchestration

When OpenClaw receives a tutoring request, the skill instructs it to use the appropriate repository adapters.

For a zero-activity request:

``` text
OpenClaw
   ↓
peppi_get_course
   ↓
peppi_get_enrolled_students
   ↓
moodle_get_activity
   ↓
find_zero_activity
   ↓
optional save_zero_activity_report
   ↓
optional MailerMock notification
```

The agent should use returned JSON as the source of truth.

If a tool reports:

``` json
{"success": false}
```

OpenClaw should report the failure rather than inventing a result.

------------------------------------------------------------------------

# 16. Persistent Zero-Activity Reports

Zero-activity reports are stored in:

``` text
reports/zero_activity_reports.json
```

The application-level behavior is append-oriented so earlier reports can be retained.

To save a report:

``` bash
python3 skills/tutor-system/tools/save_zero_activity_report.py C101
```

To inspect stored reports through the central adapter:

``` bash
python3 skills/tutor-system/scripts/tutor_tool.py zero_activity_reports C101
```

The purpose is to demonstrate that zero-activity results are persisted and can be viewed later without recalculating the entire workflow.

------------------------------------------------------------------------

# 17. Existing Deterministic Workflow

The complete repository workflow is:

``` bash
python3 scheduler/workflow.py
```

The workflow reads:

``` text
config/tutor_config.json
```

and executes enabled modules in this order:

``` text
1. Moodle progress report
2. Peppi enrichment
3. Event processing
4. Notification generation
5. Email generation
6. Optional SMTP sending
```

Generated artifacts include:

``` text
reports/student_progress_report.json
reports/peppi_enriched_report.json
events/events.json
reports/notification_queue.json
reports/generated_emails.json
reports/zero_activity_reports.json
```

For development, MailerMock is preferred over real SMTP delivery.

------------------------------------------------------------------------

# 18. Scheduling

There are two scheduling concepts in the project.

## 18.1 Repository scheduler

`scheduler/scheduler.py` uses the Python `schedule` package.

Current supported configuration includes:

``` text
daily
interval
```

The current project configuration uses:

``` text
interval: 30 seconds
```

Start it with:

``` bash
python3 scheduler/scheduler.py
```

The scheduler reads `config/tutor_config.json`.

## 18.2 OpenClaw scheduler

OpenClaw also has its own persistent cron scheduler.

List jobs:

``` bash
openclaw cron list --all
```

Create a scheduled Tutor System job:

``` bash
openclaw cron create \
  --cron "0 9 * * 1-5" \
  --tz "Europe/Helsinki" \
  --name "Tutor System Daily Test" \
  --message "Run the Tutor System zero-activity workflow." \
  --session isolated \
  --expect-final
```

After creation:

``` bash
openclaw cron list --all
```

For immediate testing:

``` bash
openclaw cron run <JOB_ID> --wait
```

View execution history:

``` bash
openclaw cron runs --id <JOB_ID> --limit 10
```

The OpenClaw cron scheduler is separate from a macOS/Linux `crontab` entry. Do not confuse the two.

------------------------------------------------------------------------

# 19. Trigger Configuration

Example trigger definitions are stored in:

``` text
config/triggers.json
```

The current examples include:

-   scheduled runs;
-   progress updates;
-   manual actions;
-   new assignment events.

These definitions describe intended trigger types. They do not replace the actual workflow/event engine.

------------------------------------------------------------------------

# 20. Testing the Configuration

## OpenClaw health

``` bash
openclaw status
```

For deeper checks:

``` bash
openclaw status --deep
```

Diagnostics:

``` bash
openclaw doctor
```

Live logs:

``` bash
openclaw logs --follow
```

## Tutor System tool test

``` bash
cd ~/openclaw-tutor
python3 skills/tutor-system/tools/find_zero_activity.py C101
```

## Full workflow test

``` bash
python3 scheduler/workflow.py
```

## Persistent report test

``` bash
python3 skills/tutor-system/tools/save_zero_activity_report.py C101
```

Then:

``` bash
python3 skills/tutor-system/scripts/tutor_tool.py zero_activity_reports C101
```

## MailerMock test

Run the appropriate notification tool and then open MailerMock to verify that the generated message appears in the recipient mailbox.

------------------------------------------------------------------------

# 21. Recommended End-to-End Demonstration

For a complete supervisor demonstration:

### Step 1 --- verify OpenClaw

``` bash
openclaw status
```

### Step 2 --- verify the mock services

Confirm:

``` text
MoodleMock  → 8000
PeppiMock   → 8001
MailerMock  → 8002
```

### Step 3 --- run a focused Tutor System request

``` bash
python3 skills/tutor-system/tools/find_zero_activity.py C101
```

### Step 4 --- persist the result

``` bash
python3 skills/tutor-system/tools/save_zero_activity_report.py C101
```

### Step 5 --- retrieve the persisted result

``` bash
python3 skills/tutor-system/scripts/tutor_tool.py zero_activity_reports C101
```

### Step 6 --- run the OpenClaw scheduled job manually

``` bash
openclaw cron run <JOB_ID> --wait
```

### Step 7 --- inspect execution history

``` bash
openclaw cron runs --id <JOB_ID> --limit 10
```

### Step 8 --- verify MailerMock

Open MailerMock and confirm that the generated teacher report or student notification is visible.

This demonstrates the complete chain:

``` text
OpenClaw
   ↓
Tutor System skill
   ↓
Python repository adapters
   ↓
PeppiMock + MoodleMock
   ↓
zero-activity analysis
   ↓
persistent report
   ↓
MailerMock
```

------------------------------------------------------------------------

# 22. Security and Secrets

Never commit:

-   Gemini API keys;
-   Telegram bot tokens;
-   OpenClaw Gateway tokens;
-   passwords;
-   real student information.

Use placeholders in documentation:

``` text
<YOUR_GEMINI_API_KEY>
<YOUR_TELEGRAM_BOT_TOKEN>
<YOUR_OPENCLAW_GATEWAY_TOKEN>
```

The mock authentication and data are for development/testing only.

The project README explicitly defines the mock environment as a prototype and not a production security mechanism.

------------------------------------------------------------------------

# 23. Troubleshooting

## Gateway is not reachable

Run:

``` bash
openclaw status
```

Then:

``` bash
openclaw logs --follow
```

Check that the Gateway is running on the configured port.

## Skill changes are not being used

Start a new OpenClaw session/turn after changing:

``` text
skills/tutor-system/SKILL.md
```

## Tool fails

Run the repository tool directly:

``` bash
python3 skills/tutor-system/tools/<tool>.py <arguments>
```

This separates an OpenClaw orchestration problem from a Python/tool implementation problem.

## Mock service unavailable

Verify the appropriate server is running and listening on its configured port.

## Emails are generated but not visible

Check:

``` text
reports/generated_emails.json
```

Then verify that MailerMock is running and refresh/reload its mailbox
data.

## Scheduled task does not appear

If using OpenClaw's scheduler:

``` bash
openclaw cron list --all
```

If using the operating-system scheduler:

``` bash
crontab -l
```

These are separate scheduling mechanisms.

------------------------------------------------------------------------

# 24. Configuration Reproduction Checklist

A new developer should be able to verify the following:

``` text
[ ] Node.js and Python installed
[ ] OpenClaw installed
[ ] openclaw --version works
[ ] openclaw configure completed
[ ] Local Gateway is running
[ ] Gateway is reachable
[ ] Gemini configured (if used)
[ ] Ollama configured (if used)
[ ] Telegram configured (if used)
[ ] openclaw-tutor repository available
[ ] Tutor System skill available
[ ] Mock services running
[ ] Mock UIs running if required
[ ] tutor_config.json reviewed
[ ] focused Tutor System tools work
[ ] zero-activity workflow works
[ ] zero-activity result persists
[ ] MailerMock receives generated messages
[ ] OpenClaw cron job can be listed
[ ] OpenClaw cron job can be manually executed
[ ] cron execution history can be inspected
[ ] no secrets committed to Git
```

------------------------------------------------------------------------

# 25. Current Configuration Reference

The current working setup was reconstructed from the project's
configuration and OpenClaw installation.

``` text
OpenClaw version: 2026.5.12
Gateway mode: local
Gateway port: 18789
Gateway authentication: token
Tailscale exposure: off

Primary AI model:
google/gemini-2.5-flash

Ollama:
enabled
endpoint: http://127.0.0.1:11434

Telegram:
enabled

Tutor System skill:
tutor-system

Repository:
~/openclaw-tutor

Tutor configuration:
config/tutor_config.json

Trigger definitions:
config/triggers.json

Central tool adapter:
skills/tutor-system/scripts/tutor_tool.py

Focused tools:
skills/tutor-system/tools/

Persistent zero-activity reports:
reports/zero_activity_reports.json
```

The actual Gateway token, Gemini API key, and Telegram bot token are intentionally omitted.

------------------------------------------------------------------------

# 26. Architecture Principle

The most important design principle of this prototype is the separation
between **AI orchestration** and **deterministic application logic**.

OpenClaw is responsible for:

-   understanding a user's tutoring request;
-   deciding which repository capability is appropriate;
-   orchestrating multiple tools;
-   generating natural-language responses;
-   optionally launching scheduled tasks;
-   communicating through configured channels such as Telegram.

The Python repository is responsible for:

-   reading mock educational data;
-   deterministic comparisons;
-   calculating zero-activity students;
-   generating reports;
-   storing persistent results;
-   generating mock email messages.

This makes the system easier to test, debug, reproduce, and demonstrate.

It also means that anyone can run the Python workflow independently to verify the underlying functionality and then use OpenClaw to demonstrate the agent/orchestration layer.

------------------------------------------------------------------------

# 27. Reproduction Summary

The shortest reproducible sequence is:

``` bash
# 1. Install OpenClaw
npm install -g openclaw

# 2. Configure OpenClaw
openclaw configure

# 3. Verify OpenClaw
openclaw status

# 4. Enter the project
cd ~/openclaw-tutor

# 5. Install project dependencies
npm install

# 6. Start the mock services in separate terminals
python3 mocks/moodlemock/server.py
python3 mocks/peppimock/server.py
python3 mocks/lianamailermock/server.py

# 7. Test a Tutor System tool
python3 skills/tutor-system/tools/find_zero_activity.py C101

# 8. Persist a result
python3 skills/tutor-system/tools/save_zero_activity_report.py C101

# 9. View the persistent result
python3 skills/tutor-system/scripts/tutor_tool.py zero_activity_reports C101

# 10. Verify OpenClaw cron configuration
openclaw cron list --all
```

For a clean reproduction, replace all secrets with the supervisor's own
credentials and use the mock services rather than real educational
systems.
