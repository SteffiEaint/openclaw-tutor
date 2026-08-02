import json
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
GENERATED_EMAILS_PATH = BASE_DIR / "reports" / "generated_emails.json"
EMAIL_LOG_PATH = BASE_DIR / "reports" / "sent_emails_log.json"
EMAIL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

# Helpers
def load_generated_emails():
    with open(GENERATED_EMAILS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_email_log(log):
    with open(EMAIL_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4)

# Fake sender
def send_email(email):

    print("\n========================================")
    print("Sending Email...")
    print("----------------------------------------")

    print(f"To: {email['to']}")
    print(f"Subject: {email['subject']}")
    print()

    print(email["body"])
    print("----------------------------------------")

    print("Status: SENT (MailerMock)")
    print("========================================")

    return {
        "recipient": email["to"],
        "subject": email["subject"],
        "status": "sent",
        "sent_at": datetime.now().isoformat(),
        "email_type": email["type"]
    }


# Main
def send_all_emails():
    emails = load_generated_emails()
    log = []
    all_emails = (
        emails["student_emails"]
        + emails["teacher_summary_emails"]
    )

    print(f"\nFound {len(all_emails)} emails.\n")

    for email in all_emails:
        result = send_email(email)
        log.append(result)
    save_email_log(log)

    print(f"\nEmail log saved to:\n{EMAIL_LOG_PATH}")


if __name__ == "__main__":
    send_all_emails()