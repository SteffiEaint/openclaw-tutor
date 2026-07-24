                Scheduler
                    │
                    ▼
             Trigger Engine
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 Scheduled      Progress      Manual/Telegram
      │             │             │
      └─────────────┼─────────────┘
                    ▼
              MoodleMock
                    ▼
          student_progress.json
                    ▼
              PeppiMock
                    ▼
      enriched_student_report.json
                    ▼
          Notification Engine
                    ▼
      teacher_emails.json
      student_emails.json
                    ▼
             MailerMock