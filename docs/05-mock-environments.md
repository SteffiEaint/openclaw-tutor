# Mock Environment Guide

The project uses three complementary mock services rather than one large simulated application.

## 1. MoodleMock — learning activity

MoodleMock represents the learning management system.

It provides:

- student accounts;
- teacher accounts;
- courses;
- course ownership through `teacherId`;
- student enrollments;
- assignments;
- completion records;
- assignment submission behavior.

## 2. PeppiMock — institutional context

PeppiMock represents student/institutional information.

It provides:

- student profiles;
- teacher profiles;
- course context;
- course URLs;
- student/teacher role-specific views;
- administrator view.

The enrichment workflow uses PeppiMock to attach identity and teacher information to Moodle progress data.

## 3. MailerMock — communication

MailerMock represents the email service.

It provides:

- student and teacher accounts;
- sign-in using known mock emails;
- inbox;
- sent mail;
- compose;
- reply;
- contacts;
- locally persisted JSON messages;
- import of generated OpenClaw email.

## Shared identity model

The same mock identities should be reused across services. A student email in MoodleMock should correspond to the same student email in PeppiMock and MailerMock. Likewise, teacher emails should remain consistent.

This consistency is essential for realistic end-to-end testing.

## Shared course model

MoodleMock owns the primary course/enrollment relationships. A course contains a `teacherId`, and that teacher relationship is used by the teacher-facing views and Peppi enrichment.

## Authentication model

Authentication is intentionally simplified. A correct mock email identifies a known account, while the password is not treated as a real credential. This is appropriate for a prototype but must never be presented as production authentication.

## Why this separation matters

Separating the services makes it possible to demonstrate realistic integration boundaries:

```text
Moodle data → Peppi context → notification decision → Mailer delivery
```

It also allows each service to be tested independently.
