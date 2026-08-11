# MailerMock Guide

## Purpose

MailerMock provides a local, browser-accessible representation of an email service so that the tutoring workflow can be demonstrated without relying on an external mailbox.

## Accounts

Valid accounts are derived from the mock student and teacher identities. A user signs in with the email already present in the mock data.

Passwords are intentionally not validated in the prototype.

## Mailbox features

The UI provides:

- inbox;
- sent mail;
- message reading;
- unread state;
- compose;
- reply;
- contacts;
- sign out;
- account information.

## Generated OpenClaw email

MailerMock imports messages from `reports/generated_emails.json` into the recipient's inbox. This means the automated workflow can produce a message without using a real SMTP server.

Example flow:

```text
Notification Engine
       ↓
notification_queue.json
       ↓
Email generation
       ↓
generated_emails.json
       ↓
MailerMock ingestion
       ↓
student@example.com inbox
```

## Manual email

A signed-in student or teacher can compose a message to another known mock user. MailerMock validates that the recipient belongs to the mock environment.

## Persistence

Messages are stored in `mocks/lianamailermock/emails.json`.

This makes the mailbox state easy to inspect and reset, but it is not a production mail store.

## Suggested end-to-end test

1. Run the workflow.
2. Confirm `reports/generated_emails.json` contains messages.
3. Start MailerMock.
4. Sign in as a recipient.
5. Open Inbox.
6. Confirm the generated message appears.
7. Open the message.
8. Reply to the sender or another valid mock account.
9. Sign in as the recipient/sender in another browser session if desired.
10. Confirm the message appears in Sent/Inbox as expected.
