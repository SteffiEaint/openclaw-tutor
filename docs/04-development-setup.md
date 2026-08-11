# Development Setup

## Prerequisites

Recommended local environment:

- Python 3.x;
- Node.js and npm;
- a browser such as Chrome/Chromium;
- Git;
- optional: Ollama for local AI model experiments;
- optional: access to Gemini or another permitted cloud provider for model comparison.

## Repository structure

```text
openclaw-tutor/
├── config/
├── docs/
├── events/
├── mocks/
│   ├── moodlemock/
│   ├── peppimock/
│   └── lianamailermock/
├── reports/
├── scheduler/
├── scripts/
├── tests/
└── ui/
    ├── moodlemock/
    ├── peppimock/
    └── mailermock/
```

## Install root test dependencies

From the project root:

```bash
npm install
```

The root package is primarily used for Playwright testing.

## Install UI dependencies

Each Vite UI is a separate frontend package. Run `npm install` inside each UI directory when required:

```bash
cd ui/moodlemock && npm install
cd ../peppimock && npm install
cd ../mailermock && npm install
```

The scaffolding helper is `install_ui_scaffolding.sh`. It copies the Vite package files for PeppiMock and MailerMock into a target project.

## Start mock services

The current Python services use these ports:

| Service | Port | Purpose |
|---|---:|---|
| MoodleMock | 8000 | Learning data and Moodle-style UI/API |
| PeppiMock | 8001 | Institutional/student/teacher context |
| MailerMock | 8002 | Mock email service |

Example:

```bash
python mocks/moodlemock/server.py
python mocks/peppimock/server.py
python mocks/lianamailermock/server.py
```

Run each server in a separate terminal.

## Start UIs

From each UI directory:

```bash
npm run dev
```

Vite will print the local development URL.

## Run the automation workflow

From the repository root:

```bash
python scheduler/workflow.py
```

This runs enabled modules in the order configured in `config/tutor_config.json`.

## Run tests

Python tests:

```bash
python -m pytest tests/test_json_utils.py
```

Playwright tests:

```bash
npm test
```

For interactive/headed execution:

```bash
npm run test:headed
npm run test:ui
```

## Configuration

`config/tutor_config.json` controls module execution and scheduler behavior. `config/triggers.json` defines example trigger types.

## Development rule

Keep generated artifacts separate from source data. Reports and event snapshots are useful for demonstrations, but source JSON files under `mocks/` should remain the canonical mock datasets.
