import hashlib
import json
import mimetypes
from datetime import datetime, timezone
from email.utils import format_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
MAILER_DIR = ROOT / "mocks" / "lianamailermock"
MOODLE_DIR = ROOT / "mocks" / "moodlemock"
PEPPI_DIR = ROOT / "mocks" / "peppimock"
UI_DIR = ROOT / "ui" / "mailermock"
HOST = "127.0.0.1"
PORT = 8002
EMAILS = MAILER_DIR / "emails.json"
USERS = MAILER_DIR / "users.json"

SYSTEM_USER = {"id": "SYSTEM", "name": "OpenClaw Tutor", "email": "openclaw@tutormock.local", "role": "system"}


def load_json(path, default=None):
    if not path.exists():
        return [] if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return [] if default is None else default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def users():
    """MailerMock is the authoritative mock identity directory."""
    return load_json(USERS, [])


def find_user(email):
    value = str(email or "").strip().lower()
    return next((u for u in users() if str(u.get("email", "")).lower() == value), None)


def message_key(message):
    raw = "|".join(str(message.get(k, "")) for k in ("from", "to", "subject", "body"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def ingest_generated_emails():
    stored = load_json(EMAILS)
    keys = {m.get("sourceKey") for m in stored}
    generated = load_json(ROOT / "reports" / "generated_emails.json", {})
    now = datetime.now(timezone.utc).isoformat()

    for category in ("student_emails", "teacher_summary_emails"):
        for email in generated.get(category, []):
            # emailId is unique per workflow run. This is deliberately used
            # instead of the email content so identical reminders generated
            # on different runs appear as separate messages in MailerMock.
            email_id = email.get("emailId")
            key = str(email_id) if email_id else message_key(email)
            message = {
                "id": f"AUTO-{key}",
                "from": SYSTEM_USER["email"],
                "fromName": SYSTEM_USER["name"],
                "to": email.get("to", ""),
                "subject": email.get("subject", "(No subject)"),
                "body": email.get("body", ""),
                "status": "delivered",
                "source": "OpenClaw workflow",
                "createdAt": email.get("generatedAt", now),
                "workflowRunId": email.get("workflowRunId"),
                "emailId": email_id,
                "read": False,
            }
            if key in keys:
                continue
            message["sourceKey"] = key
            stored.append(message)
            keys.add(key)

    save_json(EMAILS, stored)
    return stored


def all_messages():
    return ingest_generated_emails()


def send_json(handler, data, status=200):
    payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(payload)


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        send_json(self, {}, 204)

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        query = urlparse(self.path).query
        params = dict(part.split("=", 1) for part in query.split("&") if "=" in part)
        messages = all_messages()
        known_users = users()

        if path == "/api/data":
            send_json(self, {
                "users": known_users,
                "systemUser": SYSTEM_USER,
                "messages": messages,
                "templates": [
                    {"id": "progress", "name": "Progress update", "subject": "Your learning progress", "body": "Hello,\n\nHere is an update about your learning progress.\n\nBest regards,\nOpenClaw Tutor"},
                    {"id": "reminder", "name": "Assignment reminder", "subject": "Assignment reminder", "body": "Hello,\n\nThis is a reminder about an upcoming assignment.\n\nBest regards,\nOpenClaw Tutor"},
                ],
            })
            return

        if path.startswith("/api/mailbox/"):
            email = unquote(path.split("/api/mailbox/", 1)[1]).strip().lower()
            if not find_user(email):
                send_json(self, {"error": "Mailbox not found"}, 404)
                return
            inbox = [m for m in messages if m.get("to", "").lower() == email]
            sent = [m for m in messages if m.get("from", "").lower() == email]
            send_json(self, {"email": email, "inbox": inbox, "sent": sent})
            return

        if path == "/api/users":
            send_json(self, {"users": known_users})
            return

        if path.startswith("/api/users/by-email/"):
            email = unquote(path.split("/api/users/by-email/", 1)[1]).strip().lower()
            user = find_user(email)
            if not user:
                send_json(self, {"exists": False, "error": "User not found"}, 404)
                return
            send_json(self, {"exists": True, "user": user})
            return

        if path == "/":
            path = "/index.html"
        file_path = UI_DIR / path.lstrip("/")
        if file_path.is_file():
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", mimetypes.guess_type(str(file_path))[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        send_json(self, {"error": "Not found"}, 404)

    def do_POST(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            send_json(self, {"error": "Invalid JSON"}, 400)
            return

        if path == "/api/login":
            user = find_user(body.get("email"))
            if not user:
                send_json(self, {"success": False, "error": "No MailerMock account found for this email."}, 401)
                return
            send_json(self, {"success": True, "user": user})
            return

        if path == "/api/send":
            sender = find_user(body.get("from"))
            recipient = find_user(body.get("to"))
            if not sender:
                send_json(self, {"error": "Sender mailbox not found"}, 401)
                return
            if not recipient:
                send_json(self, {"error": "Recipient must be a valid student or teacher email in the mock environment."}, 400)
                return
            subject = str(body.get("subject", "")).strip() or "(No subject)"
            message = {
                "id": f"MAIL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
                "from": sender["email"],
                "fromName": sender["name"],
                "to": recipient["email"],
                "toName": recipient["name"],
                "subject": subject,
                "body": str(body.get("body", "")),
                "status": "delivered",
                "source": "MailerMock user",
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "read": False,
            }
            messages = load_json(EMAILS)
            messages.append(message)
            save_json(EMAILS, messages)
            send_json(self, {"success": True, "message": message}, 201)
            return

        if path.startswith("/api/read/"):
            message_id = unquote(path.split("/api/read/", 1)[1])
            messages = load_json(EMAILS)
            message = next((m for m in messages if m.get("id") == message_id), None)
            if not message:
                send_json(self, {"error": "Message not found"}, 404)
                return
            message["read"] = True
            save_json(EMAILS, messages)
            send_json(self, {"success": True, "message": message})
            return

        send_json(self, {"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print(f"[MailerMock] {format % args}")


def main():
    MAILER_DIR.mkdir(parents=True, exist_ok=True)
    if not EMAILS.exists():
        save_json(EMAILS, [])
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"MailerMock running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
