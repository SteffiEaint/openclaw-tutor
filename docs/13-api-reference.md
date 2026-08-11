# Mock API Reference

This reference describes the main HTTP endpoints exposed by the current mock services.

## MoodleMock — port 8000

### `GET /api/data`

Returns the main MoodleMock dataset, including students, courses, enrollments, assignments, completions, and teacher information used by the service.

### `GET /api/student/<id-or-email>`

Returns a student-specific view containing the student's account, enrolled courses, assignments, and completion records.

### `GET /api/teacher/<id-or-email>`

Returns a teacher-specific view containing the teacher and the courses/students associated with the teacher.

### `GET /api/course/<courseId>`

Returns course information and related assignment/enrollment information.

### `POST /api/login`

Request body:

```json
{
  "email": "student@example.com",
  "password": "anything"
}
```

A valid mock email is sufficient to identify the account. The password is intentionally not validated.

### `POST /api/submit/<assignmentId>`

Request body:

```json
{
  "studentId": "S001"
}
```

Marks the student's completion record as completed and records the submission time.

### `POST /api/run-workflow`

Provides a local workflow trigger endpoint in the MoodleMock service for demonstration/integration purposes.

## PeppiMock — port 8001

### `GET /api/data`

Returns available PeppiMock data.

### `GET /api/student/<id-or-email>`

Returns a student profile and related study information.

### `GET /api/teacher/<id-or-email>`

Returns teacher information, courses taught, enrollments, and students associated with those courses.

### `GET /api/course/<courseId>`

Returns course context.

### `POST /api/login`

Authenticates a known student, teacher, or prototype administrator by email.

## MailerMock — port 8002

### `GET /api/data`

Returns mock mail-service data/summary.

### `GET /api/users`

Returns valid mock student and teacher mailbox accounts.

### `GET /api/mailbox/<email>`

Returns inbox and sent messages for a known mailbox.

### `POST /api/login`

Logs in a known mock mailbox account by email.

### `POST /api/send`

Sends a message from the signed-in mock account to another valid mock account.

### `POST /api/read/<messageId>`

Marks a message as read.

## API design limitations

These APIs are intentionally simple. They do not provide real authentication tokens, authorization middleware, database transactions, rate limiting, or production-grade validation.
