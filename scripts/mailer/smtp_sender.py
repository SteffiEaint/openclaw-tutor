import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent.parent
GENERATED_EMAILS_PATH = BASE_DIR / "reports" / "generated_emails.json"
EMAIL_LOG_PATH = BASE_DIR / "reports" / "sent_emails_log.json"
EMAIL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def load_generated_emails():
    if not GENERATED_EMAILS_PATH.exists():
        return {"student_emails": [], "teacher_summary_emails": []}
    with open(GENERATED_EMAILS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_email_log():
    if not EMAIL_LOG_PATH.exists():
        return []
    try:
        with open(EMAIL_LOG_PATH, "r", encoding="utf-8") as f:
            value = json.load(f)
            return value if isinstance(value, list) else []
    except json.JSONDecodeError:
        return []


def save_email_log(log):
    with open(EMAIL_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=4, ensure_ascii=False)


def email_fingerprint(email):
    # A generated email gets a unique emailId for each workflow run.
    # Fall back to content for older generated files.
    if email.get("emailId"):
        return str(email["emailId"])

    raw = "|".join([
        str(email.get("to", "")).strip().lower(),
        str(email.get("subject", "")).strip(),
        str(email.get("body", "")).strip(),
        str(email.get("type", "")).strip(),
    ])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def send_email(email):
    print("\n========================================")
    print("Sending Email...")
    print("----------------------------------------")
    print(f"To: {email['to']}")
    print(f"Subject: {email['subject']}")
    print()
    print(email['body'])
    print("----------------------------------------")
    print("Status: SENT (MailerMock)")
    print("========================================")

    return {
        "recipient": email["to"],
        "subject": email["subject"],
        "status": "sent",
        "sent_at": datetime.now(timezone.utc).isoformat(),
        "email_type": email["type"],
        "fingerprint": email_fingerprint(email),
        "email_id": email.get("emailId"),
        "workflow_run_id": email.get("workflowRunId"),
    }


def send_all_emails():
    emails = load_generated_emails()
    log = load_email_log()
    known = {item.get("fingerprint") for item in log if item.get("fingerprint")}
    # Backward compatibility with old logs that predate fingerprints.
    all_emails = emails.get("student_emails", []) + emails.get("teacher_summary_emails", [])
    print(f"\nFound {len(all_emails)} generated emails.")

    added = 0
    skipped = 0
    for email in all_emails:
        fingerprint = email_fingerprint(email)
        if fingerprint in known:
            skipped += 1
            continue
        result = send_email(email)
        log.append(result)
        known.add(fingerprint)
        added += 1

    save_email_log(log)
    print(f"\nNewly recorded: {added}")
    print(f"Already recorded/skipped: {skipped}")
    print(f"Total persistent email log entries: {len(log)}")
    print(f"Email log saved to: {EMAIL_LOG_PATH}")


if __name__ == "__main__":
    send_all_emails()
