# Project Overview

## Project title

**OpenClaw Tutor — AI-Assisted Student Progress Monitoring and Communication**

## Purpose

The project investigates whether an AI-powered tutor/assistant can support students and teachers by connecting educational data, progress analysis, notifications, and communication workflows.

The prototype is designed around OpenClaw as the AI-agent/workflow layer and uses local mock services so that the system can be developed without depending on production Moodle, Peppi, or mail infrastructure.

## Core question

> Can an AI tutor become a useful companion for students during periods when teachers have limited availability, while reducing repetitive monitoring and reporting work for teachers?

## Main actors

### Student

A student can:

- sign in to MoodleMock using the email stored in the mock dataset;
- view enrolled courses;
- inspect assignments and deadlines;
- view progress;
- submit a mock assignment;
- use PeppiMock to view personal study information;
- use MailerMock to receive and send mock email.

### Teacher

A teacher can:

- sign in to MoodleMock;
- view courses they teach;
- view students enrolled in those courses;
- inspect course progress;
- use PeppiMock to view teacher/course information;
- use MailerMock to receive generated reports and communicate with mock users.

### Administrator

PeppiMock includes an administrator role for inspecting the simulated student, teacher, course, and enrollment environment. This is an administrative mock role rather than a production identity-management system.

### OpenClaw / automation layer

The automation layer consumes mock educational data, produces reports, detects events, builds notification queues, and generates email content.

## Prototype scope

The current repository contains:

- Moodle-style student and teacher data;
- Peppi-style student and teacher data;
- course and enrollment relationships;
- assignment and completion tracking;
- event detection;
- student progress reporting;
- Peppi enrichment;
- notification generation;
- student and teacher email generation;
- MailerMock storage and mailbox UI;
- scheduling support;
- Playwright and Python tests.

## Explicit non-goals

The prototype does not attempt to provide:

- production authentication;
- production-grade authorization/security;
- a real Moodle integration;
- a real Peppi integration;
- a production SMTP service;
- persistent database infrastructure;
- production-scale reliability;
- autonomous educational decision-making without human oversight.

## Design principle

The prototype should demonstrate a complete workflow rather than production readiness:

**Educational data → event/progress analysis → enrichment → notification decision → email generation → mock mailbox**
