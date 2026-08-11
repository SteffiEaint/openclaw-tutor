import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[2]
PEPPI_DIR = ROOT / "mocks" / "peppimock"
MOODLE_DIR = ROOT / "mocks" / "moodlemock"
UI_DIR = ROOT / "ui" / "peppimock"
HOST = "127.0.0.1"
PORT = 8001


def load_json(path, default=None):
    if not path.exists():
        return [] if default is None else default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[PeppiMock] Could not read {path}: {exc}")
        return [] if default is None else default


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


def moodle_data():
    return {
        "students": load_json(MOODLE_DIR / "students.json"),
        "courses": load_json(MOODLE_DIR / "courses.json"),
        "enrollments": load_json(MOODLE_DIR / "enrollments.json"),
    }


def peppi_data():
    md = moodle_data()
    students = load_json(PEPPI_DIR / "students.json")
    teachers = load_json(PEPPI_DIR / "teachers.json")
    urls = load_json(PEPPI_DIR / "course_urls.json")
    url_map = {x.get("course_id"): x.get("course_url") for x in urls}
    teacher_map = {x.get("teacher_id"): x for x in teachers}

    courses = []
    for course in md["courses"]:
        teacher = teacher_map.get(course.get("teacherId"), {})
        courses.append({
            **course,
            "teacherName": teacher.get("teacher_name"),
            "teacherEmail": teacher.get("teacher_email"),
            "courseUrl": url_map.get(course.get("courseId")),
        })

    course_map = {c["courseId"]: c for c in courses}
    student_map = {s.get("studentId"): s for s in students}

    enrollments = []
    for enrollment in md["enrollments"]:
        course = course_map.get(enrollment.get("courseId"), {})
        student = student_map.get(enrollment.get("studentId"), {})
        enrollments.append({
            **enrollment,
            "courseName": course.get("courseName"),
            "teacherId": course.get("teacherId"),
            "teacherName": course.get("teacherName"),
            "studentName": student.get("name"),
            "studentEmail": student.get("email"),
            "status": enrollment.get("status", "Enrolled"),
        })

    # A lightweight Peppi-style study-right record derived from enrollment.
    study_rights = [
        {
            "studyRightId": f"SR-{e['enrollmentId']}",
            "studentId": e["studentId"],
            "courseId": e["courseId"],
            "courseName": e.get("courseName"),
            "status": "Active",
        }
        for e in enrollments
    ]

    return {
        "students": students,
        "teachers": teachers,
        "courses": courses,
        "enrollments": enrollments,
        "studyRights": study_rights,
        "programs": [],
        "courseUrls": urls,
    }



MAILER_AUTH_URL = "http://127.0.0.1:8002/api/users/by-email/"

def verify_mailer_identity(email):
    url = MAILER_AUTH_URL + quote(email, safe="")
    try:
        with urlopen(Request(url, method="GET"), timeout=2.0) as response:
            return json.loads(response.read().decode("utf-8")).get("user")
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return None

def find_user(data, identifier):
    value = unquote(identifier).strip().lower()
    student = next((s for s in data["students"] if value in {str(s.get("studentId", "")).lower(), str(s.get("email", "")).lower()}), None)
    if student:
        return "student", student
    teacher = next((t for t in data["teachers"] if value in {str(t.get("teacher_id", "")).lower(), str(t.get("teacher_email", "")).lower()}), None)
    if teacher:
        return "teacher", teacher
    if value == "admin@peppimock.local":
        return "admin", {"adminId": "ADMIN001", "name": "Peppi Administrator", "email": "admin@peppimock.local"}
    return None, None


class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        send_json(self, {}, 204)

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        data = peppi_data()

        if path == "/api/data":
            send_json(self, data)
            return

        if path.startswith("/api/student/"):
            role, student = find_user(data, path.split("/api/student/", 1)[1])
            if role != "student":
                send_json(self, {"error": "Student not found"}, 404)
                return
            sid = student["studentId"]
            enrollments = [e for e in data["enrollments"] if e["studentId"] == sid]
            send_json(self, {"success": True, "student": student, "courses": [c for c in data["courses"] if c["courseId"] in {e["courseId"] for e in enrollments}], "enrollments": enrollments, "studyRights": [r for r in data["studyRights"] if r["studentId"] == sid]})
            return

        if path.startswith("/api/teacher/"):
            role, teacher = find_user(data, path.split("/api/teacher/", 1)[1])
            if role != "teacher":
                send_json(self, {"error": "Teacher not found"}, 404)
                return
            tid = teacher["teacher_id"]
            courses = [c for c in data["courses"] if c.get("teacherId") == tid]
            course_ids = {c["courseId"] for c in courses}
            enrollments = [e for e in data["enrollments"] if e["courseId"] in course_ids]
            students = [s for s in data["students"] if s["studentId"] in {e["studentId"] for e in enrollments}]
            send_json(self, {"success": True, "teacher": teacher, "courses": courses, "students": students, "enrollments": enrollments})
            return

        if path.startswith("/api/course/"):
            cid = unquote(path.split("/api/course/", 1)[1])
            course = next((c for c in data["courses"] if c["courseId"] == cid), None)
            if not course:
                send_json(self, {"error": "Course not found"}, 404)
                return
            send_json(self, {"success": True, "course": course, "enrollments": [e for e in data["enrollments"] if e["courseId"] == cid]})
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
            data = peppi_data()
            email = str(body.get("email", "")).strip().lower()
            identity = verify_mailer_identity(email)
            if identity is None:
                send_json(self, {"success": False, "error": "MailerMock could not verify this email. Make sure MailerMock is running and the account exists there."}, 503)
                return

            if identity.get("role") == "admin" and email == "admin@peppimock.local":
                account = {"adminId": "ADMIN001", "name": "Peppi Administrator", "email": email}
                send_json(self, {"success": True, "role": "admin", "account": account})
                return

            role, account = find_user(data, email)
            if account and role == identity.get("role") and str(account.get("studentId") or account.get("teacher_id")) == str(identity.get("id")):
                send_json(self, {"success": True, "role": role, "account": account})
                return

            send_json(self, {"success": False, "error": "The MailerMock account exists, but the corresponding PeppiMock record is missing."}, 404)
            return
        send_json(self, {"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print(f"[PeppiMock] {format % args}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"PeppiMock running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
