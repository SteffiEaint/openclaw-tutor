# Mock Authentication Architecture

The three mock applications use MailerMock as the authoritative mock identity directory.

## Identity source

`mocks/lianamailermock/users.json` contains the mock accounts used by the system. Each account has:

- `id` — shared student/teacher identifier
- `name`
- `email`
- `role`

The current directory contains all 20 students, the three teachers, and the Peppi administrator account.

## Login flow

### MailerMock

MailerMock checks the email directly against `users.json`.

### MoodleMock

MoodleMock sends the submitted email to MailerMock's `/api/users/by-email/<email>` endpoint first. If the identity exists, MoodleMock verifies that the same ID and email exist in its own Moodle data and then loads the student's or teacher's Moodle record.

### PeppiMock

PeppiMock uses the same process. It asks MailerMock to verify the identity, then loads the corresponding student, teacher, or administrator record from PeppiMock data.

## Passwords

Passwords are intentionally not validated in this prototype. Any password can be entered once the email belongs to a registered mock account.

## Required startup order

Start MailerMock before MoodleMock or PeppiMock so their login requests can verify identities:

```bash
python mocks/lianamailermock/server.py
python ui/moodlemock/server.py
python mocks/peppimock/server.py
```

Then start each Vite UI in its own terminal as usual.

## Adding a new student

A new student must have the same ID and email in all relevant mock data sources. Add the identity to:

`mocks/lianamailermock/users.json`

and add the corresponding student record to the MoodleMock and PeppiMock student data. Once those records exist, the same email can be used to sign in to all three systems.
