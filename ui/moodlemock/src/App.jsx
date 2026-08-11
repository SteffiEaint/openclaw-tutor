import React, { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

function App() {
    const [data, setData] = useState(null);
    const [session, setSession] = useState(null);
    const [sessionData, setSessionData] = useState(null);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const [loginLoading, setLoginLoading] = useState(false);
    const [page, setPage] = useState("dashboard");
    const [selectedCourse, setSelectedCourse] = useState(null);
    const [selectedAssignment, setSelectedAssignment] = useState(null);

    async function fetchData() {
        const response = await fetch(`${API}/api/data`);
        if (!response.ok) throw new Error("MoodleMock data could not be loaded.");
        return response.json();
    }

    async function loadAccount(currentSession, currentData = data) {
        const endpoint = currentSession.role === "teacher"
            ? `${API}/api/teacher/${encodeURIComponent(currentSession.id)}`
            : `${API}/api/student/${encodeURIComponent(currentSession.id)}`;
        const response = await fetch(endpoint);
        if (!response.ok) throw new Error("Account data could not be loaded.");
        const result = await response.json();
        setSessionData(result);
        setSession(currentSession);
        if (currentData) setData(currentData);
    }

    useEffect(() => {
        let active = true;
        async function initialize() {
            try {
                const result = await fetchData();
                if (!active) return;
                setData(result);
                const saved = localStorage.getItem("moodlemock_session");
                if (saved) {
                    const parsed = JSON.parse(saved);
                    if (parsed?.id && parsed?.role) {
                        try {
                            await loadAccount(parsed, result);
                        } catch {
                            localStorage.removeItem("moodlemock_session");
                        }
                    }
                }
            } catch (err) {
                console.error(err);
                setError("MoodleMock is unavailable. Start the MoodleMock server and refresh.");
            } finally {
                if (active) setLoading(false);
            }
        }
        initialize();
        return () => { active = false; };
    }, []);

    async function handleLogin(event) {
        event.preventDefault();
        setError("");
        setLoginLoading(true);
        try {
            const response = await fetch(`${API}/api/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const result = await response.json();
            if (!response.ok || !result.success) throw new Error(result.error || "Login failed.");
            const account = result.account;
            const currentSession = result.role === "teacher"
                ? { id: account.teacher_id, role: "teacher", email: account.teacher_email }
                : { id: account.studentId, role: "student", email: account.email };
            await loadAccount(currentSession, data);
            localStorage.setItem("moodlemock_session", JSON.stringify(currentSession));
            setPage("dashboard");
            setSelectedCourse(null);
            setSelectedAssignment(null);
            setPassword("");
        } catch (err) {
            console.error(err);
            setError(err.message || "Unable to log in.");
        } finally {
            setLoginLoading(false);
        }
    }

    function logout() {
        localStorage.removeItem("moodlemock_session");
        setSession(null);
        setSessionData(null);
        setEmail("");
        setPassword("");
        setPage("dashboard");
        setSelectedCourse(null);
        setSelectedAssignment(null);
    }

    async function refreshAccount() {
        if (!session) return;
        try { await loadAccount(session, data); } catch (err) { console.error(err); }
    }

    if (loading) return <Loading title="Loading MoodleMock..." text="Connecting to the mock learning environment." />;
    if (!data) return <ErrorScreen message={error} onRetry={() => window.location.reload()} />;
    if (!session || !sessionData) {
        return <LoginPage email={email} password={password} setEmail={setEmail} setPassword={setPassword} error={error} loading={loginLoading} onLogin={handleLogin} students={data.students || []} teachers={data.teachers || []} />;
    }

    const isTeacher = session.role === "teacher";
    const account = isTeacher ? sessionData.teacher : sessionData.student;
    const courses = sessionData.courses || [];
    const assignments = sessionData.assignments || [];
    const completions = sessionData.completions || [];
    const completionMap = Object.fromEntries(completions.map(c => [c.assignmentId, c]));

    function courseWithProgress(course) {
        const items = assignments.filter(a => a.courseId === course.courseId);
        const completed = items.filter(a => completionMap[a.assignmentId]?.status === "completed").length;
        return { ...course, assignments: items, completed, percentage: items.length ? Math.round(completed / items.length * 100) : 0 };
    }
    const courseProgress = isTeacher
        ? courses.map(course => {
            const enrolledIds = new Set((sessionData.enrollments || [])
                .filter(e => e.courseId === course.courseId)
                .map(e => e.studentId));
            const enrolledStudents = (sessionData.studentProgress || [])
                .filter(s => enrolledIds.has(s.studentId));
            const percentage = enrolledStudents.length
                ? Math.round(enrolledStudents.reduce((sum, s) => sum + (s.progressPercentage || 0), 0) / enrolledStudents.length)
                : 0;
            return {
                ...course,
                assignments: assignments.filter(a => a.courseId === course.courseId),
                percentage,
            };
        })
        : courses.map(courseWithProgress);

    function openCourse(course) { setSelectedCourse(course); setPage("course"); }
    function openAssignment(assignment) { setSelectedAssignment(assignment); setPage("assignment"); }

    return (
        <div className="app">
            <header className="topbar">
                <button className="brand" onClick={() => setPage("dashboard")}>
                    <span className="brand-mark">M</span>
                    <span><strong>MoodleMock</strong><small>Learning platform</small></span>
                </button>
                <div className="topbar-actions">
                    <span className={`role-pill ${isTeacher ? "teacher" : "student"}`}>{isTeacher ? "Teacher" : "Student"}</span>
                    <button className="user-chip" onClick={logout} title="Log out">
                        <span className="avatar">{initials(account)}</span>
                        <span>{displayName(account)}</span><span>↪</span>
                    </button>
                </div>
            </header>

            <div className="layout">
                <aside className="sidebar">
                    <nav>
                        <NavButton active={page === "dashboard"} onClick={() => setPage("dashboard")} icon="⌂">Dashboard</NavButton>
                        <NavButton active={page === "courses"} onClick={() => setPage("courses")} icon="▦">My courses</NavButton>
                        {isTeacher && <NavButton active={page === "students"} onClick={() => setPage("students")} icon="♙">My students</NavButton>}
                        {!isTeacher && <NavButton active={page === "calendar"} onClick={() => setPage("calendar")} icon="◷">Calendar</NavButton>}
                        {!isTeacher && <NavButton active={page === "grades"} onClick={() => setPage("grades")} icon="%">Progress</NavButton>}
                    </nav>
                    <div className="sidebar-divider" />
                    <div className="sidebar-heading">{isTeacher ? "Courses I teach" : "My courses"}</div>
                    {courseProgress.map(course => <button className="course-nav-item" key={course.courseId} onClick={() => openCourse(course)}><span className="course-dot" />{course.courseName}</button>)}
                    <div className="sidebar-footer"><strong>MoodleMock</strong><span>Mock learning environment</span><button className="text-button" onClick={logout}>Log out</button></div>
                </aside>

                <main className="main-content">
                    {page === "dashboard" && (isTeacher
                        ? <TeacherDashboard account={account} courses={courseProgress} students={sessionData.studentProgress || []} onCourse={openCourse} onStudents={() => setPage("students")} />
                        : <StudentDashboard account={account} courses={courseProgress} completions={completions} assignments={assignments} completionMap={completionMap} onCourse={openCourse} onAssignment={openAssignment} />
                    )}
                    {page === "courses" && <CoursesPage courses={courseProgress} onCourse={openCourse} teacher={isTeacher} />}
                    {page === "students" && isTeacher && <TeacherStudentsPage students={sessionData.studentProgress || []} />}
                    {page === "course" && selectedCourse && <CoursePage course={selectedCourse} completionMap={completionMap} onBack={() => setPage("courses")} onAssignment={openAssignment} teacher={isTeacher} />}
                    {page === "assignment" && selectedAssignment && <AssignmentPage assignment={selectedAssignment} completion={completionMap[selectedAssignment.assignmentId]} student={account} teacher={isTeacher} onBack={() => setPage(selectedCourse ? "course" : "dashboard")} onSubmitted={refreshAccount} />}
                    {page === "calendar" && !isTeacher && <CalendarPage assignments={assignments} completionMap={completionMap} onAssignment={openAssignment} />}
                    {page === "grades" && !isTeacher && <GradesPage courses={courseProgress} />}
                </main>
            </div>
        </div>
    );
}

function LoginPage({ email, password, setEmail, setPassword, error, loading, onLogin, students, teachers }) {
    const examples = [...students.slice(0, 3), ...teachers.slice(0, 2)];
    return <div className="login-screen"><div className="login-card">
        <div className="login-logo">M</div><h1>MoodleMock</h1><p className="login-subtitle">Student and teacher learning environment</p>
        <form onSubmit={onLogin}>
            <label>Email address</label><input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="student@example.com" required />
            <label>Password</label><input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Any password in this mock" />
            {error && <div className="login-error">{error}</div>}
            <button className="primary-button" disabled={loading}>{loading ? "Signing in..." : "Log in"}</button>
        </form>
        <div className="demo-accounts"><strong>Mock accounts</strong><p>Use any student or teacher email from the dataset. Passwords are intentionally not validated.</p>
            <div className="demo-buttons">{examples.map(user => <button key={user.studentId || user.teacher_id} type="button" onClick={() => setEmail(user.email || user.teacher_email)}>{user.studentId || user.teacher_id}</button>)}</div>
        </div>
    </div></div>;
}

function StudentDashboard({ account, courses, completions, assignments, completionMap, onCourse, onAssignment }) {
    const completed = completions.filter(c => c.status === "completed").length;
    const missing = completions.filter(c => c.status === "missing").length;
    const upcoming = assignments.filter(a => completionMap[a.assignmentId]?.status !== "completed").sort((a,b) => new Date(a.dueDate)-new Date(b.dueDate)).slice(0,6);
    return <><PageHeader eyebrow="Dashboard" title={`Welcome back, ${firstName(account)}`} description="Your MoodleMock learning progress at a glance." />
        <div className="stats-grid"><StatCard icon="✓" value={completed} label="Completed" /><StatCard icon="!" value={missing} label="Missing" danger /><StatCard icon="▦" value={courses.length} label="Courses" /><StatCard icon="◷" value={upcoming.length} label="Needs attention" /></div>
        <div className="dashboard-grid"><section className="panel"><PanelHeader title="My courses" subtitle="Current progress" /><div className="course-list">{courses.map(c => <CourseCard key={c.courseId} course={c} onClick={() => onCourse(c)} />)}</div></section>
        <section className="panel"><PanelHeader title="Upcoming work" subtitle="Assignments requiring attention" /><div className="assignment-list">{upcoming.map(a => <AssignmentRow key={a.assignmentId} assignment={a} status={completionMap[a.assignmentId]?.status} onClick={() => onAssignment(a)} />)}{!upcoming.length && <Empty text="You are all caught up." />}</div></section></div></>;
}

function TeacherDashboard({ account, courses, students, onCourse, onStudents }) {
    const atRisk = students.filter(s => s.progressPercentage === 0).length;
    return <><PageHeader eyebrow="Teacher dashboard" title={`Welcome, ${firstName(account)}`} description="Monitor the courses you teach and the students enrolled in them." />
        <div className="stats-grid"><StatCard icon="▦" value={courses.length} label="Courses I teach" /><StatCard icon="♙" value={students.length} label="Students" /><StatCard icon="!" value={atRisk} label="0% progress" danger /><StatCard icon="✓" value={`${averageProgress(students)}%`} label="Average progress" /></div>
        <div className="dashboard-grid"><section className="panel"><PanelHeader title="Courses I teach" subtitle="Managed courses" /><div className="course-list">{courses.map(c => <CourseCard key={c.courseId} course={c} onClick={() => onCourse(c)} />)}</div></section>
        <section className="panel"><PanelHeader title="Students needing attention" subtitle="Lowest progress first" /><div className="assignment-list">{[...students].sort((a,b) => a.progressPercentage-b.progressPercentage).slice(0,7).map(s => <div className="student-progress-row" key={s.studentId}><div className="avatar small">{initials(s)}</div><div><strong>{s.name}</strong><span>{s.email}</span></div><b>{s.progressPercentage}%</b></div>)}</div><button className="text-button panel-action" onClick={onStudents}>View all students →</button></section></div></>;
}

function CoursesPage({ courses, onCourse, teacher }) { return <><PageHeader eyebrow="Courses" title={teacher ? "Courses I teach" : "My courses"} description={teacher ? "Courses and students under your teaching responsibility." : "Courses you are enrolled in."} /><div className="large-course-grid">{courses.map(c => <CourseCard key={c.courseId} course={c} large onClick={() => onCourse(c)} />)}</div></>; }
function TeacherStudentsPage({ students }) { return <><PageHeader eyebrow="Students" title="My students" description="Students enrolled in the courses you teach." /><div className="student-table">{students.map(s => <div className="table-row" key={s.studentId}><div className="student-cell"><span className="avatar small">{initials(s)}</span><span><strong>{s.name}</strong><small>{s.email}</small></span></div><span>{(s.courseIds || []).join(", ") || "—"}</span><strong>{s.progressPercentage}%</strong></div>)}</div></>; }

function CoursePage({ course, completionMap, onBack, onAssignment, teacher }) { return <><button className="back-button" onClick={onBack}>← Back</button><div className="course-header"><div className="course-header-code">{course.courseCode || course.courseId}</div><div><h1>{course.courseName}</h1><p>{teacher ? "Course you manage" : "Course workspace"}</p></div></div><div className="course-progress-panel"><div><strong>Course progress</strong><span>{course.percentage}%</span></div><div className="progress-track large"><div className="progress-fill" style={{width: `${course.percentage}%`}} /></div></div><div className="section-title"><h2>{teacher ? "Assignments" : "Activities"}</h2><span>{course.assignments.length} activities</span></div><div className="activity-list">{course.assignments.map(a => <button className="activity-item" key={a.assignmentId} onClick={() => onAssignment(a)}><div className="activity-icon">📝</div><div className="activity-main"><h3>{a.title}</h3><p>{a.description || "Assignment"}</p><span>Due {formatDate(a.dueDate)}</span></div>{!teacher && <StatusBadge status={completionMap[a.assignmentId]?.status} />}<span className="chevron">→</span></button>)}</div></>; }

function AssignmentPage({ assignment, completion, student, teacher, onBack, onSubmitted }) {
    const [submitting, setSubmitting] = useState(false);
    async function submit() { if (teacher) return; setSubmitting(true); try { const r = await fetch(`${API}/api/submit/${assignment.assignmentId}`, { method: "POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify({studentId: student.studentId}) }); if (!r.ok) throw new Error("Submission failed"); await onSubmitted(); } catch (e) { console.error(e); alert(e.message); } finally { setSubmitting(false); } }
    const completed = completion?.status === "completed";
    return <><button className="back-button" onClick={onBack}>← Back</button><div className="assignment-detail"><div className="assignment-detail-header"><span className="assignment-type">Assignment</span><h1>{assignment.title}</h1><p>Due {formatDate(assignment.dueDate)}</p></div><div className="assignment-content"><section className="assignment-description"><h2>Assignment information</h2><p>{assignment.description || "Complete this assignment according to the course instructions."}</p></section><aside className="submission-card"><span>Submission status</span><h3>{teacher ? "Teacher view" : completed ? "Completed" : "Not submitted"}</h3>{!teacher && !completed && <button className="primary-button" onClick={submit} disabled={submitting}>{submitting ? "Submitting..." : "Submit assignment"}</button>}{!teacher && completed && <div className="success-message">✓ Assignment submitted</div>}{completion?.submittedAt && <div className="submitted-date">Submitted {formatDateTime(completion.submittedAt)}</div>}</aside></div></div></>;
}

function CalendarPage({ assignments, completionMap, onAssignment }) { return <><PageHeader eyebrow="Calendar" title="Calendar" description="Assignment deadlines and activities." /><div className="calendar-panel">{[...assignments].sort((a,b)=>new Date(a.dueDate)-new Date(b.dueDate)).map(a => <button className="calendar-event" key={a.assignmentId} onClick={() => onAssignment(a)}><div className="calendar-date">{new Date(a.dueDate).getDate()}</div><div><strong>{a.title}</strong><span>Due {formatDate(a.dueDate)}</span></div><StatusBadge status={completionMap[a.assignmentId]?.status}/></button>)}</div></>; }
function GradesPage({ courses }) { return <><PageHeader eyebrow="Progress" title="Course progress" description="Your current completion percentage by course." /><div className="grades-panel">{courses.map(c => <div className="grade-row" key={c.courseId}><div><strong>{c.courseName}</strong><small>{c.courseId}</small></div><div className="progress-track large"><div className="progress-fill" style={{width:`${c.percentage}%`}}/></div><strong>{c.percentage}%</strong></div>)}</div></>; }

function CourseCard({ course, onClick, large=false }) { return <button className={large ? "large-course-card" : "course-card"} onClick={onClick}><div className={large ? "large-course-banner" : "course-banner"}>{course.courseCode || course.courseId}</div><div className={large ? "large-course-body" : "course-card-body"}><h3>{course.courseName}</h3><div className="progress-row"><div className="progress-track"><div className="progress-fill" style={{width:`${course.percentage}%`}}/></div><span>{course.percentage}%</span></div><span className="course-link">Open course →</span></div></button>; }
function AssignmentRow({ assignment, status, onClick }) { return <button className="assignment-row" onClick={onClick}><div className="assignment-icon">📝</div><div className="assignment-info"><strong>{assignment.title}</strong><span>Due {formatDate(assignment.dueDate)}</span></div><StatusBadge status={status}/></button>; }
function NavButton({ active, onClick, icon, children }) { return <button className={`nav-item ${active ? "active" : ""}`} onClick={onClick}><span>{icon}</span>{children}</button>; }
function PageHeader({ eyebrow, title, description }) { return <div className="page-header"><div className="breadcrumb">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>; }
function PanelHeader({ title, subtitle }) { return <div className="panel-header"><div><h2>{title}</h2><p>{subtitle}</p></div></div>; }
function StatCard({ icon, value, label, danger=false }) { return <div className={`stat-card ${danger ? "danger" : ""}`}><div className="stat-icon">{icon}</div><div><div className="stat-value">{value}</div><div className="stat-label">{label}</div></div></div>; }
function StatusBadge({ status }) { if (!status) return null; const labels={completed:"Completed",missing:"Missing",late:"Late","in-progress":"In progress"}; return <span className={`status-badge status-${status}`}>{labels[status] || status}</span>; }
function Empty({ text }) { return <div className="empty-state">{text}</div>; }
function Loading({ title, text }) { return <div className="loading-screen"><div className="loading-logo">M</div><h2>{title}</h2><p>{text}</p></div>; }
function ErrorScreen({ message, onRetry }) { return <div className="loading-screen"><div className="loading-logo error">!</div><h2>MoodleMock unavailable</h2><p>{message}</p><button className="primary-button compact" onClick={onRetry}>Retry</button></div>; }
function displayName(account) { return account?.name || `${account?.firstName || ""} ${account?.lastName || ""}`.trim() || account?.teacher_name || "User"; }
function firstName(account) { return displayName(account).split(" ")[0]; }
function initials(account) { const name=displayName(account).split(" ").filter(Boolean); return `${name[0]?.[0] || ""}${name[1]?.[0] || ""}`.toUpperCase(); }
function averageProgress(students) { if (!students.length) return 0; return Math.round(students.reduce((sum,s)=>sum+(s.progressPercentage||0),0)/students.length); }
function formatDate(value) { return value ? new Date(value).toLocaleDateString("en-GB", {day:"numeric",month:"short",year:"numeric"}) : "No date"; }
function formatDateTime(value) { return value ? new Date(value).toLocaleString("en-GB", {day:"numeric",month:"short",year:"numeric",hour:"2-digit",minute:"2-digit"}) : "Unknown"; }

export default App;
