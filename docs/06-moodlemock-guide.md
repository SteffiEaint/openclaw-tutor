# MoodleMock Guide

## Purpose

MoodleMock simulates the part of a learning management system that the AI tutor needs to observe and interact with.

## Student functionality

Students can:

- sign in using their dataset email;
- view dashboard statistics;
- view enrolled courses;
- inspect assignments;
- see completion status;
- see upcoming/missing work;
- view calendar information;
- view course progress;
- submit assignments.

## Teacher functionality

Teachers can sign in using their teacher email. A teacher sees courses where the course's `teacherId` matches the teacher's ID.

Teacher views are intended to support:

- course management overview;
- enrolled-student visibility;
- progress monitoring;
- assignment context;
- identification of students needing attention.

## Data files

| File | Meaning |
|---|---|
| `students.json` | Student identity data |
| `courses.json` | Courses and teacher ownership |
| `enrollments.json` | Student-course relationships |
| `assignments.json` | Assignment definitions and due dates |
| `assignmentCompletions.json` | Student assignment state |

## Assignment submission

The UI sends a POST request to `/api/submit/<assignmentId>` with the student ID. MoodleMock changes the completion status to `completed` and records `submittedAt`.

The event engine can later detect that status transition.

## Important behavior

MoodleMock does not continuously watch JSON files for changes in the background. The event engine is responsible for comparing current data with snapshots and detecting changes when it runs.

This distinction is important when explaining the system:

> The mock LMS stores state; the event engine detects changes between workflow runs.

## Suggested student test

1. Sign in as a student.
2. Open a course.
3. Open an incomplete assignment.
4. Submit it.
5. Run the event engine.
6. Confirm an `assignment_completed` event is produced when the state transition is detected.
7. Run the progress report again.
8. Confirm the student's course progress increases.

## Suggested teacher test

1. Sign in using a teacher email.
2. Confirm only the teacher's courses are visible.
3. Open a course.
4. Review enrolled students.
5. Identify a low-progress student.
6. Run the reporting/notification workflow.
7. Confirm the generated teacher report/email references the correct course and students.
