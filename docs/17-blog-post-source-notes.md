# Blog Post Source Notes

This document is intended to support the final non-technical blog article. The blog should explain the project to ordinary readers rather than reproduce implementation details.

## Possible title

**Can an AI Tutor Help Students During the Summer?**

## Opening problem

Students may continue studying while teachers have limited availability. A useful assistant could help monitor progress and provide reminders without replacing teachers.

## Explain the idea simply

Instead of presenting OpenClaw as a collection of technical components, describe it as the system that helps an AI model use information and tools to perform useful tasks.

## Explain the three mock systems

Use everyday analogies:

- **MoodleMock** — the classroom/learning platform;
- **PeppiMock** — the school office/student information system;
- **MailerMock** — the school's mailbox.

The interesting part is what happens when these systems work together.

## Example story

A student has several unfinished assignments.

1. MoodleMock contains the assignment and completion information.
2. The workflow calculates the student's progress.
3. PeppiMock supplies the student's and teacher's context.
4. The notification system decides that a reminder may be useful.
5. An email is generated.
6. MailerMock places it in the student's inbox.
7. A teacher can also receive a summary.

This is much easier for a general audience to understand than a list of Python scripts.

## Human role

Emphasize that the goal is not to replace teachers. Teachers still provide:

- judgement;
- encouragement;
- subject expertise;
- mentoring;
- human relationships.

AI is being investigated as a support tool for repetitive monitoring and communication.

## Challenges worth discussing

- AI models do not always behave consistently.
- Integrating several systems is harder than using one chatbot.
- Local AI models require hardware resources.
- Cloud AI can introduce usage limits and costs.
- Automation requires careful testing.
- Mock environments simplify development but do not perfectly represent production systems.

## Good visual material for the blog

Capture screenshots of:

- MoodleMock student dashboard;
- MoodleMock teacher dashboard;
- PeppiMock student/teacher page;
- MailerMock inbox containing an automatically generated reminder;
- a simple architecture diagram;
- an example progress report.

Avoid screenshots containing real personal information or API keys.

## Closing question

End by returning to the original question: is the AI tutor becoming genuinely useful, or is it still mainly an interesting technical experiment?
