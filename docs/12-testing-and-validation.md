# Testing and Validation

## Testing strategy

The project uses multiple layers of testing.

### Python unit tests

The repository contains Python tests such as `tests/test_json_utils.py` for utility behavior.

### Playwright tests

The Playwright suite covers scenarios including:

- completion behavior;
- new assignments;
- overdue assignments;
- workflow behavior.

Relevant files include:

- `tests/completion.spec.ts`;
- `tests/new_assignment.spec.ts`;
- `tests/overdue.spec.ts`;
- `tests/workflow.spec.ts`.

## Recommended end-to-end test matrix

| Scenario | Expected result |
|---|---|
| Student login with valid email | Student dashboard opens |
| Teacher login with valid email | Teacher dashboard opens |
| Unknown Moodle email | Login rejected |
| Student opens own course | Course is visible |
| Teacher opens course | Only managed courses are visible |
| Student submits assignment | Completion becomes completed |
| Workflow runs after submission | Completion event can be detected |
| Assignment due date passes | In-progress item can become missing |
| New assignment is added | New-assignment event can be detected |
| Progress report runs | `student_progress_report.json` updates |
| Peppi enrichment runs | Student/teacher context is added |
| Notification engine runs | Notification queue is produced |
| Email generation runs | Generated messages are produced |
| MailerMock opens recipient inbox | Generated email is visible |
| User sends manual email | Recipient can see message |

## Manual regression checklist

Before a major demonstration:

1. Start all three mock servers.
2. Start all three UIs if they are separate from the servers.
3. Verify student login.
4. Verify teacher login.
5. Verify Peppi student and teacher views.
6. Run the workflow.
7. Inspect generated reports.
8. Open MailerMock as a recipient.
9. Verify generated email.
10. Run Playwright tests.
11. Record screenshots and failures.

## What to measure

For the final evaluation, record:

- workflow execution time;
- number of students processed;
- number of courses processed;
- number of notifications generated;
- number of emails generated;
- AI model response time where applicable;
- AI model cost where applicable;
- local-model hardware usage where applicable;
- false positives/irrelevant notifications observed during testing.

## Test evidence

Keep screenshots, test output, and representative JSON artifacts for the final report. Do not include sensitive real-world data.
