import json
import sys
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts" / "util"))

from scripts.util.json_utils import load_json, count_completed_assignments  # noqa: E402


MOCK_DIR = REPO_ROOT / "mocks" / "moodlemock"


# ---------------------------------------------------------------------------
# count_completed_assignments — pure logic, no file I/O needed
# ---------------------------------------------------------------------------

def test_count_completed_assignments_basic():
    data = [
        {"studentId": "S001", "status": "completed"},
        {"studentId": "S001", "status": "late"},
        {"studentId": "S002", "status": "completed"},
    ]
    result = count_completed_assignments(data)
    assert result == {"S001": 1, "S002": 1}


def test_count_completed_assignments_multiple_per_student():
    data = [
        {"studentId": "S001", "status": "completed"},
        {"studentId": "S001", "status": "completed"},
        {"studentId": "S001", "status": "completed"},
    ]
    result = count_completed_assignments(data)
    assert result == {"S001": 3}


def test_count_completed_assignments_ignores_non_completed_statuses():
    data = [
        {"studentId": "S001", "status": "late"},
        {"studentId": "S001", "status": "in-progress"},
        {"studentId": "S001", "status": "missing"},
    ]
    result = count_completed_assignments(data)
    assert result == {}


def test_count_completed_assignments_skips_missing_student_id():
    data = [
        {"status": "completed"},  # no studentId at all
        {"studentId": "", "status": "completed"},  # falsy studentId
        {"studentId": "S001", "status": "completed"},
    ]
    result = count_completed_assignments(data)
    assert result == {"S001": 1}


def test_count_completed_assignments_empty_input():
    assert count_completed_assignments([]) == {}


def test_count_completed_assignments_does_not_mutate_input():
    data = [{"studentId": "S001", "status": "completed"}]
    original = json.loads(json.dumps(data))  # deep copy for comparison
    count_completed_assignments(data)
    assert data == original


# ---------------------------------------------------------------------------
# load_json — file I/O against the real mock data directory
# ---------------------------------------------------------------------------

@pytest.fixture
def chdir_repo_root(monkeypatch):
    """load_json resolves paths relative to the current working directory,
    so tests that exercise it need cwd set to the repo root."""
    monkeypatch.chdir(REPO_ROOT)


def test_load_json_returns_list(chdir_repo_root):
    data = load_json("students.json")
    assert isinstance(data, list)
    assert len(data) > 0


def test_load_json_missing_file_raises(chdir_repo_root):
    with pytest.raises(FileNotFoundError):
        load_json("does_not_exist.json")


def test_load_json_assignment_completions_filename_matches_mock_dir(chdir_repo_root):
    """Regression test: the loader previously pointed at 'completions.json',
    which does not exist. The real file is 'assignmentCompletions.json'."""
    data = load_json("assignmentCompletions.json")
    assert isinstance(data, list)
    assert len(data) > 0
    assert "studentId" in data[0]
    assert "status" in data[0]


# ---------------------------------------------------------------------------
# Integration: load_json + count_completed_assignments against real mock data
# ---------------------------------------------------------------------------

def test_end_to_end_against_real_mock_data(chdir_repo_root):
    completions_data = load_json("assignmentCompletions.json")
    result = count_completed_assignments(completions_data)

    # Every student in the result should have a positive completed count
    assert all(count > 0 for count in result.values())

    # Cross-check against a manual count straight from the raw file
    manual_counts = {}
    for record in completions_data:
        if record.get("status") == "completed":
            sid = record["studentId"]
            manual_counts[sid] = manual_counts.get(sid, 0) + 1

    assert result == manual_counts