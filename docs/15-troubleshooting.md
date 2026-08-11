# Troubleshooting Guide

## MoodleMock shows a blank page

If React reports:

```text
Rendered more hooks than during the previous render
```

this indicates that a React hook such as `useMemo`, `useEffect`, or `useState` is being called conditionally. All hooks must execute in the same order on every render.

Fix by moving hooks above conditional returns such as login/loading screens.

## UI loads but data is missing

Check:

1. MoodleMock server is running on port 8000.
2. Browser console for failed `fetch()` requests.
3. `/api/data` returns JSON.
4. JSON source files exist and are valid.

## Login fails

The prototype uses email identity matching. Confirm the email exists exactly in the relevant mock dataset, ignoring capitalization and surrounding whitespace.

Passwords are intentionally not validated.

## Teacher sees no courses

Check that the teacher's ID matches the course's `teacherId`.

For example:

```text
teachers.json
teacher_id = T001

courses.json
teacherId = T001
```

## Peppi enrichment is empty

Run the Moodle report first:

```bash
python scripts/moodle/generate_student_progress_report.py
```

Then run:

```bash
python scripts/peppi/enrich_with_peppi.py
```

Also verify student IDs match between MoodleMock and PeppiMock.

## MailerMock inbox is empty

Check:

1. `reports/generated_emails.json` exists.
2. Generated email `to` addresses match a MailerMock user email.
3. MailerMock server is running.
4. MailerMock can read `mocks/lianamailermock/emails.json`.
5. The browser is calling port 8002.

## Events are not detected immediately

The system is snapshot-based. Editing a JSON file does not automatically create an event. Run the event engine/workflow after the change.

## Assignment does not become missing

Verify:

- completion status is `in-progress`;
- assignment has a valid UTC due date;
- current time is later than the due date;
- the event engine has been run.

## Playwright fails because a service is unavailable

Start the required mock service(s) before running browser tests. Review the Playwright configuration and test helpers for expected URLs.

## npm files are missing

`npm install` creates `node_modules` and uses `package.json` as its manifest. If a directory only contains `src/`, the package scaffolding was not copied there yet. Run the UI scaffolding script or create/copy the UI package files before installing dependencies.

## Large ZIP files

Do not include `node_modules`, `.git`, test reports, or caches when creating a project ZIP for sharing. They can be recreated from `package-lock.json` and `package.json`.
