# PeppiMock Guide

## Purpose

PeppiMock simulates institutional information that is useful for enriching learning data. It should be thought of as a student information/study management system rather than another Moodle instance.

## Roles

### Student

A student can sign in with their mock email and inspect personal information and study/course context.

### Teacher

A teacher can sign in with their teacher email and view courses they teach and the students enrolled in those courses.

### Administrator

The mock administrator can inspect broader student, teacher, course, and enrollment information.

The administrator account is a prototype-only account and is not intended to represent real institutional authentication.

## Data relationship

PeppiMock uses student and teacher records while course/enrollment relationships are aligned with MoodleMock. This reduces the risk of a progress report referring to the wrong teacher or student.

## Enrichment role

The script `scripts/peppi/enrich_with_peppi.py` reads the Moodle progress report and adds:

- student name;
- student email;
- teacher name;
- teacher email;
- course name;
- course URL.

The resulting file is `reports/peppi_enriched_report.json`.

## Why enrichment is useful

Moodle progress data alone may contain identifiers such as `S003` and `C103`. Enrichment turns those identifiers into information that is more useful for a human-facing notification:

```text
S003 / C103
      ↓
Charlie Brown / World History I / Dr. Brown / brown@test.fi
```

## Suggested test scenarios

- student login by email;
- teacher login by email;
- administrator login;
- teacher sees only their courses;
- teacher sees students in those courses;
- course URLs match the course being displayed;
- enrichment output contains both student and teacher information.
