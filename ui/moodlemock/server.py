import json
import mimetypes
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[2]
MOODLE_DIR = ROOT / "mocks" / "moodlemock"
PEPPI_DIR = ROOT / "mocks" / "peppimock"
UI_DIR = ROOT / "ui" / "moodlemock"

HOST = "127.0.0.1"
PORT = 8000

STUDENTS = MOODLE_DIR / "students.json"
COURSES = MOODLE_DIR / "courses.json"
ENROLLMENTS = MOODLE_DIR / "enrollments.json"
ASSIGNMENTS = MOODLE_DIR / "assignments.json"
COMPLETIONS = MOODLE_DIR / "assignmentCompletions.json"
TEACHERS = PEPPI_DIR / "teachers.json"


def load_json(path, default=None):
    if not path.exists():
        return [] if default is None else default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[MoodleMock] Could not read {path}: {exc}")
        return [] if default is None else default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def read_data():
    return {
        "students": load_json(STUDENTS),
        "courses": load_json(COURSES),
        "enrollments": load_json(ENROLLMENTS),
        "assignments": load_json(ASSIGNMENTS),
        "completions": load_json(COMPLETIONS),
        "teachers": load_json(TEACHERS),
    }


def send_json(handler, data, status=200):
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(payload)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(payload)


def find_student(data, identifier):
    value = unquote(identifier).strip().lower()
    return next(
        (s for s in data["students"] if value in {
            str(s.get("studentId", "")).lower(),
            str(s.get("email", "")).lower(),
        }),
        None,
    )


def find_teacher(data, identifier):
    value = unquote(identifier).strip().lower()
    return next(
        (t for t in data["teachers"] if value in {
            str(t.get("teacher_id", "")).lower(),
            str(t.get("teacher_email", "")).lower(),
        }),
        None,
    )


def student_payload(data, student):
    sid = student["studentId"]
    enrollments = [e for e in data["enrollments"] if e["studentId"] == sid]
    course_ids = {e["courseId"] for e in enrollments}
    courses = [c for c in data["courses"] if c["courseId"] in course_ids]
    assignments = [
        a for a in data["assignments"]
        if a["courseId"] in course_ids and not a["assignmentId"].startswith("ATEST")
    ]
    completions = [c for c in data["completions"] if c["studentId"] == sid]
    return {
        "student": student,
        "courses": courses,
        "assignments": assignments,
        "completions": completions,
        "enrollments": enrollments,
    }


def teacher_payload(data, teacher):
    tid = teacher["teacher_id"]
    courses = [c for c in data["courses"] if c.get("teacherId") == tid]
    course_ids = {c["courseId"] for c in courses}
    enrollments = [e for e in data["enrollments"] if e["courseId"] in course_ids]
    student_ids = {e["studentId"] for e in enrollments}
    students = [s for s in data["students"] if s["studentId"] in student_ids]
    assignments = [
        a for a in data["assignments"]
        if a["courseId"] in course_ids and not a["assignmentId"].startswith("ATEST")
    ]
    completions = [c for c in data["completions"] if c["studentId"] in student_ids and any(
        a["assignmentId"] == c["assignmentId"] for a in assignments
    )]

    progress = []
    for student in students:
        sid = student["studentId"]
        enrolled_course_ids = {e["courseId"] for e in enrollments if e["studentId"] == sid}
        student_assignments = [a for a in assignments if a["courseId"] in enrolled_course_ids]
        student_completions = {c["assignmentId"]: c for c in completions if c["studentId"] == sid}
        completed = sum(
            student_completions.get(a["assignmentId"], {}).get("status") == "completed"
            for a in student_assignments
        )
        progress.append({
            **student,
            "courseIds": sorted(enrolled_course_ids),
            "assignmentCount": len(student_assignments),
            "completedCount": completed,
            "progressPercentage": round((completed / len(student_assignments)) * 100, 2) if student_assignments else 0,
        })

    return {
        "teacher": teacher,
        "courses": courses,
        "students": students,
        "studentProgress": progress,
        "assignments": assignments,
        "completions": completions,
        "enrollments": enrollments,
    }


class MoodleMockHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        send_json(self, {}, 204)

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        data = read_data()

        if path == "/api/data":
            send_json(self, data)
            return

        if path.startswith("/api/student/"):
            student = find_student(data, path.split("/api/student/", 1)[1])
            if not student:
                send_json(self, {"error": "Student not found"}, 404)
                return
            send_json(self, student_payload(data, student))
            return

        if path.startswith("/api/teacher/"):
            teacher = find_teacher(data, path.split("/api/teacher/", 1)[1])
            if not teacher:
                send_json(self, {"error": "Teacher not found"}, 404)
                return
            send_json(self, teacher_payload(data, teacher))
            return

        if path.startswith("/api/course/"):
            course_id = unquote(path.split("/api/course/", 1)[1])
            course = next((c for c in data["courses"] if c["courseId"] == course_id), None)
            if not course:
                send_json(self, {"error": "Course not found"}, 404)
                return
            assignments = [a for a in data["assignments"] if a["courseId"] == course_id and not a["assignmentId"].startswith("ATEST")]
            enrollments = [e for e in data["enrollments"] if e["courseId"] == course_id]
            students = [s for s in data["students"] if s["studentId"] in {e["studentId"] for e in enrollments}]
            send_json(self, {"course": course, "assignments": assignments, "enrollments": enrollments, "students": students})
            return

        if path == "/":
            path = "/index.html"
        file_path = UI_DIR / path.lstrip("/")
        if file_path.is_file():
            content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
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

        data = read_data()

        if path == "/api/login":
            email = str(body.get("email", "")).strip().lower()
            student = next((s for s in data["students"] if s.get("email", "").lower() == email), None)
            if student:
                send_json(self, {"success": True, "role": "student", "account": student})
                return
            teacher = next((t for t in data["teachers"] if t.get("teacher_email", "").lower() == email), None)
            if teacher:
                send_json(self, {"success": True, "role": "teacher", "account": teacher})
                return
            send_json(self, {"success": False, "error": "No Moodle account found for this email."}, 401)
            return

        if path.startswith("/api/submit/"):
            assignment_id = unquote(path.split("/api/submit/", 1)[1])
            student_id = body.get("studentId")
            if not student_id:
                send_json(self, {"error": "studentId is required"}, 400)
                return
            completions = data["completions"]
            completion = next((c for c in completions if c["studentId"] == student_id and c["assignmentId"] == assignment_id), None)
            if not completion:
                send_json(self, {"error": "Completion record not found"}, 404)
                return
            completion["status"] = "completed"
            completion["submittedAt"] = datetime.now(timezone.utc).isoformat()
            save_json(COMPLETIONS, completions)
            send_json(self, {"success": True, "completion": completion})
            return

        if path == "/api/run-workflow":
            try:
                result = subprocess.run(["python", "scheduler/workflow.py"], cwd=ROOT, capture_output=True, text=True, check=True)
                send_json(self, {"success": True, "output": result.stdout, "error": result.stderr})
            except subprocess.CalledProcessError as exc:
                send_json(self, {"success": False, "output": exc.stdout, "error": exc.stderr}, 500)
            return

        send_json(self, {"error": "Not found"}, 404)

    def log_message(self, format, *args):
        print(f"[MoodleMock] {format % args}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), MoodleMockHandler)
    print(f"MoodleMock running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
