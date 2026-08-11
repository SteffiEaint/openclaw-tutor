import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8001";

function App() {
    const [data, setData] = useState(null);
    const [session, setSession] = useState(null);
    const [accountData, setAccountData] = useState(null);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const [loginLoading, setLoginLoading] = useState(false);
    const [page, setPage] = useState("dashboard");
    const [search, setSearch] = useState("");

    useEffect(() => {
        let active = true;

        async function initialize() {
            try {
                const result = await fetchData();
                if (!active) return;

                setData(result);

                const saved = localStorage.getItem("peppimock_session");
                if (!saved) return;

                try {
                    const savedSession = JSON.parse(saved);
                    const userExists =
                        savedSession?.role && savedSession?.id;

                    if (!userExists) {
                        localStorage.removeItem("peppimock_session");
                        return;
                    }

                    const loaded = await fetchAccountData(
                        savedSession,
                        result
                    );

                    if (!active) return;

                    setAccountData(loaded);
                    setSession(savedSession);
                } catch (err) {
                    console.error(err);
                    localStorage.removeItem("peppimock_session");
                }
            } catch (err) {
                console.error(err);
                if (active) {
                    setError(
                        err.message ||
                            "Unable to connect to PeppiMock."
                    );
                }
            } finally {
                if (active) setLoading(false);
            }
        }

        initialize();

        return () => {
            active = false;
        };
    }, []);

    async function fetchData() {
        const response = await fetch(`${API}/api/data`);

        if (!response.ok) {
            throw new Error(
                "PeppiMock is unavailable. Start the PeppiMock server and refresh."
            );
        }

        return response.json();
    }

    async function fetchAccountData(currentSession, currentData = data) {
        if (currentSession.role === "admin") {
            return {
                admin:
                    currentSession.account || {
                        adminId: "ADMIN001",
                        name: "Peppi Administrator",
                        email: "admin@peppimock.local",
                    },
                ...(currentData || {}),
            };
        }

        const endpoint =
            currentSession.role === "teacher"
                ? `${API}/api/teacher/${encodeURIComponent(currentSession.id)}`
                : `${API}/api/student/${encodeURIComponent(currentSession.id)}`;

        const response = await fetch(endpoint);

        if (!response.ok) {
            throw new Error("Peppi account data could not be loaded.");
        }

        return response.json();
    }

    async function handleLogin(event) {
        event.preventDefault();
        setError("");
        setLoginLoading(true);

        try {
            const response = await fetch(`${API}/api/login`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: email.trim(),
                    password,
                }),
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.error || "PeppiMock login failed."
                );
            }

            const account = result.account;
            let currentSession;

            if (result.role === "student") {
                currentSession = {
                    id: account.studentId,
                    role: "student",
                    email: account.email,
                    account,
                };
            } else if (result.role === "teacher") {
                currentSession = {
                    id: account.teacher_id,
                    role: "teacher",
                    email: account.teacher_email,
                    account,
                };
            } else {
                currentSession = {
                    id: account.adminId,
                    role: "admin",
                    email: account.email,
                    account,
                };
            }

            const loaded = await fetchAccountData(
                currentSession,
                data
            );

            setSession(currentSession);
            setAccountData(loaded);
            localStorage.setItem(
                "peppimock_session",
                JSON.stringify(currentSession)
            );
            setPassword("");
            setPage("dashboard");
            setSearch("");
        } catch (err) {
            console.error(err);
            setError(err.message || "Unable to log in.");
        } finally {
            setLoginLoading(false);
        }
    }

    function logout() {
        localStorage.removeItem("peppimock_session");
        setSession(null);
        setAccountData(null);
        setEmail("");
        setPassword("");
        setPage("dashboard");
        setSearch("");
    }

    if (loading) {
        return <Loading />;
    }

    if (!data) {
        return (
            <Loading
                error={error}
                onRetry={() => window.location.reload()}
            />
        );
    }

    if (!session || !accountData) {
        return (
            <LoginPage
                email={email}
                password={password}
                setEmail={setEmail}
                setPassword={setPassword}
                error={error}
                loading={loginLoading}
                onLogin={handleLogin}
                students={data.students || []}
                teachers={data.teachers || []}
            />
        );
    }

    const role = session.role;
    const account =
        role === "student"
            ? accountData.student
            : role === "teacher"
                ? accountData.teacher
                : accountData.admin;

    const courses = accountData.courses || data.courses || [];
    const students = accountData.students || data.students || [];
    const teachers = data.teachers || [];
    const enrollments = accountData.enrollments || data.enrollments || [];
    const rights = accountData.studyRights || data.studyRights || [];

    const visibleCourseIds = new Set(
        enrollments.map((enrollment) => enrollment.courseId)
    );

    const visibleCourses =
        role === "student"
            ? courses.filter((course) =>
                  visibleCourseIds.has(course.courseId)
              )
            : courses;

    const visibleStudents =
        role === "teacher"
            ? students.filter((student) =>
                  enrollments.some(
                      (enrollment) =>
                          enrollment.studentId === student.studentId
                  )
              )
            : students;

    const teacherCourseIds = new Set(
        role === "teacher"
            ? courses.map((course) => course.courseId)
            : []
    );

    const teacherEnrollments =
        role === "teacher"
            ? enrollments.filter((enrollment) =>
                  teacherCourseIds.has(enrollment.courseId)
              )
            : enrollments;

    return (
        <div className="app">
            <header className="topbar">
                <button
                    className="brand"
                    type="button"
                    onClick={() => setPage("dashboard")}
                >
                    <span className="logo">P</span>
                    <span>
                        <strong>PeppiMock</strong>
                        <small>Student information system</small>
                    </span>
                </button>

                <div className="topbar-right">
                    <span className={`role-pill ${role}`}>
                        {role}
                    </span>
                    <button
                        className="user-chip"
                        type="button"
                        onClick={logout}
                        title="Sign out"
                    >
                        <span className="avatar">
                            {initials(account)}
                        </span>
                        <span>{nameOf(account)}</span>
                        <span>↪</span>
                    </button>
                </div>
            </header>

            <div className="layout">
                <aside className="sidebar">
                    <nav>
                        <Nav
                            active={page === "dashboard"}
                            onClick={() => setPage("dashboard")}
                            icon="⌂"
                        >
                            Dashboard
                        </Nav>

                        {role === "student" && (
                            <>
                                <Nav
                                    active={page === "profile"}
                                    onClick={() => setPage("profile")}
                                    icon="◉"
                                >
                                    My information
                                </Nav>
                                <Nav
                                    active={page === "courses"}
                                    onClick={() => setPage("courses")}
                                    icon="▦"
                                >
                                    My courses
                                </Nav>
                                <Nav
                                    active={page === "rights"}
                                    onClick={() => setPage("rights")}
                                    icon="✓"
                                >
                                    Study rights
                                </Nav>
                            </>
                        )}

                        {role === "teacher" && (
                            <>
                                <Nav
                                    active={page === "courses"}
                                    onClick={() => setPage("courses")}
                                    icon="▦"
                                >
                                    Courses I teach
                                </Nav>
                                <Nav
                                    active={page === "students"}
                                    onClick={() => setPage("students")}
                                    icon="♙"
                                >
                                    My students
                                </Nav>
                            </>
                        )}

                        {role === "admin" && (
                            <>
                                <Nav
                                    active={page === "students"}
                                    onClick={() => setPage("students")}
                                    icon="♙"
                                >
                                    Students
                                </Nav>
                                <Nav
                                    active={page === "teachers"}
                                    onClick={() => setPage("teachers")}
                                    icon="♙"
                                >
                                    Teachers
                                </Nav>
                                <Nav
                                    active={page === "courses"}
                                    onClick={() => setPage("courses")}
                                    icon="▦"
                                >
                                    All courses
                                </Nav>
                                <Nav
                                    active={page === "rights"}
                                    onClick={() => setPage("rights")}
                                    icon="✓"
                                >
                                    Study rights
                                </Nav>
                            </>
                        )}
                    </nav>

                    <div className="sidebar-footer">
                        <strong>PeppiMock</strong>
                        <span>Mock student information system</span>
                        <button
                            className="text-button"
                            type="button"
                            onClick={logout}
                        >
                            Log out
                        </button>
                    </div>
                </aside>

                <main className="main-content">
                    {error && (
                        <div className="global-error">{error}</div>
                    )}

                    {page === "dashboard" && (
                        <Dashboard
                            role={role}
                            account={account}
                            courses={visibleCourses}
                            students={visibleStudents}
                            enrollments={
                                role === "teacher"
                                    ? teacherEnrollments
                                    : enrollments
                            }
                            rights={rights}
                            onNavigate={setPage}
                        />
                    )}

                    {page === "profile" && role === "student" && (
                        <StudentProfile
                            student={accountData.student}
                            courses={visibleCourses}
                            rights={rights}
                        />
                    )}

                    {page === "courses" && (
                        <CoursesPage
                            courses={visibleCourses}
                            role={role}
                        />
                    )}

                    {page === "students" && (
                        <StudentsPage
                            students={visibleStudents}
                            search={search}
                            setSearch={setSearch}
                            role={role}
                            enrollments={teacherEnrollments}
                        />
                    )}

                    {page === "teachers" && role === "admin" && (
                        <TeachersPage
                            teachers={teachers}
                            courses={data.courses || []}
                        />
                    )}

                    {page === "rights" && role === "admin" && (
                        <RightsPage
                            rights={rights}
                            students={data.students || []}
                        />
                    )}
                </main>
            </div>
        </div>
    );
}

function LoginPage({
    email,
    password,
    setEmail,
    setPassword,
    error,
    loading,
    onLogin,
    students,
    teachers,
}) {
    const examples = [
        ...students.slice(0, 3),
        ...teachers.slice(0, 3),
        {
            email: "admin@peppimock.local",
            name: "Peppi Administrator",
        },
    ];

    return (
        <div className="login-screen">
            <div className="login-card">
                <div className="login-logo">P</div>
                <h1>PeppiMock</h1>
                <p>
                    Sign in to your mock student information system.
                </p>

                <form onSubmit={onLogin}>
                    <label htmlFor="peppi-email">Email address</label>
                    <input
                        id="peppi-email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        placeholder="name@example.com"
                        required
                    />

                    <label htmlFor="peppi-password">Password</label>
                    <input
                        id="peppi-password"
                        type="password"
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                        placeholder="Any password in this mock"
                    />

                    {error && <div className="login-error">{error}</div>}

                    <button
                        className="primary-button"
                        type="submit"
                        disabled={loading}
                    >
                        {loading ? "Signing in..." : "Sign in"}
                    </button>
                </form>

                <div className="demo">
                    <strong>Mock accounts</strong>
                    <p>
                        Use any student or teacher email from the dataset,
                        or the administrator account. Passwords are not
                        validated in this prototype.
                    </p>
                    <div>
                        {examples.map((example) => (
                            <button
                                key={example.email}
                                type="button"
                                onClick={() => setEmail(example.email)}
                            >
                                {example.email}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function Dashboard({
    role,
    account,
    courses,
    students,
    enrollments,
    rights,
    onNavigate,
}) {
    const average = averageProgress(students);

    return (
        <>
            <PageHeader
                eyebrow="Dashboard"
                title={`Welcome, ${firstName(account)}`}
                description={
                    role === "student"
                        ? "Your study information and enrolled courses."
                        : role === "teacher"
                            ? "Your teaching responsibilities and enrolled students."
                            : "Administrative overview of the PeppiMock environment."
                }
            />

            <div className="stats-grid">
                <Stat
                    icon="▦"
                    value={courses.length}
                    label={
                        role === "teacher"
                            ? "Courses I teach"
                            : "Courses"
                    }
                />
                <Stat
                    icon="♙"
                    value={
                        role === "student"
                            ? enrollments.length
                            : students.length
                    }
                    label={
                        role === "student"
                            ? "Enrollments"
                            : "Students"
                    }
                />
                <Stat
                    icon="✓"
                    value={
                        role === "student"
                            ? rights.length
                            : `${average}%`
                    }
                    label={
                        role === "student"
                            ? "Study rights"
                            : "Average progress"
                    }
                />
                <Stat
                    icon="◉"
                    value={role === "admin" ? "Admin" : "Active"}
                    label="Account"
                />
            </div>

            <div className="dashboard-grid">
                <section className="panel">
                    <Header
                        title={
                            role === "teacher"
                                ? "Courses I teach"
                                : "Courses"
                        }
                        subtitle="Course information connected to MoodleMock"
                    />
                    <div className="course-grid">
                        {courses.map((course) => (
                            <CourseCard
                                key={course.courseId}
                                course={course}
                            />
                        ))}
                        {!courses.length && (
                            <Empty text="No courses available." />
                        )}
                    </div>
                </section>

                <section className="panel">
                    <Header
                        title={
                            role === "student"
                                ? "My information"
                                : role === "teacher"
                                    ? "Teaching overview"
                                    : "Environment"
                        }
                        subtitle={account?.email}
                    />
                    <div className="panel-body">
                        {role === "student" && (
                            <>
                                <Info
                                    label="Student ID"
                                    value={account.studentId}
                                />
                                <Info
                                    label="Email"
                                    value={account.email}
                                />
                                <Info
                                    label="Enrolled courses"
                                    value={enrollments.length}
                                />
                            </>
                        )}

                        {role === "teacher" && (
                            <>
                                <Info
                                    label="Teacher ID"
                                    value={account.teacher_id}
                                />
                                <Info
                                    label="Email"
                                    value={account.teacher_email}
                                />
                                <Info
                                    label="Students"
                                    value={students.length}
                                />
                                <button
                                    className="text-button"
                                    type="button"
                                    onClick={() => onNavigate("students")}
                                >
                                    View my students →
                                </button>
                            </>
                        )}

                        {role === "admin" && (
                            <>
                                <Info
                                    label="Students"
                                    value={students.length}
                                />
                                <Info
                                    label="Courses"
                                    value={courses.length}
                                />
                                <Info
                                    label="Study rights"
                                    value={rights.length}
                                />
                            </>
                        )}
                    </div>
                </section>
            </div>
        </>
    );
}

function StudentProfile({ student, courses, rights }) {
    return (
        <>
            <PageHeader
                eyebrow="My information"
                title={student.name}
                description={student.email}
            />

            <div className="profile-grid">
                <section className="panel">
                    <Header title="Personal information" />
                    <div className="panel-body">
                        <Info label="Student ID" value={student.studentId} />
                        <Info label="Email" value={student.email} />
                    </div>
                </section>

                <section className="panel">
                    <Header title="Study rights" />
                    <div className="panel-body">
                        {rights.map((right) => (
                            <Record
                                key={right.studyRightId}
                                title={right.courseName}
                                value={right.status}
                            />
                        ))}
                        {!rights.length && (
                            <Empty text="No study rights found." />
                        )}
                    </div>
                </section>

                <section className="panel full">
                    <Header title="Enrolled courses" />
                    <div className="course-grid">
                        {courses.map((course) => (
                            <CourseCard
                                key={course.courseId}
                                course={course}
                            />
                        ))}
                    </div>
                </section>
            </div>
        </>
    );
}

function CoursesPage({ courses, role }) {
    return (
        <>
            <PageHeader
                eyebrow="Courses"
                title={role === "teacher" ? "Courses I teach" : "Courses"}
                description={
                    role === "teacher"
                        ? "Courses assigned to your teacher account."
                        : "Courses associated with your study record."
                }
            />

            <div className="course-grid large">
                {courses.map((course) => (
                    <CourseCard
                        key={course.courseId}
                        course={course}
                        large
                    />
                ))}
                {!courses.length && (
                    <Empty text="No courses available." />
                )}
            </div>
        </>
    );
}

function StudentsPage({
    students,
    search,
    setSearch,
    role,
    enrollments,
}) {
    const query = search.trim().toLowerCase();
    const filtered = students.filter((student) =>
        JSON.stringify(student).toLowerCase().includes(query)
    );

    return (
        <>
            <PageHeader
                eyebrow="Students"
                title={role === "teacher" ? "My students" : "Student directory"}
                description={
                    role === "teacher"
                        ? "Students enrolled in the courses you teach."
                        : "Student records available to the administrator."
                }
            />

            <input
                className="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search name, ID or email..."
            />

            <div className="list">
                {filtered.map((student) => (
                    <div className="list-row" key={student.studentId}>
                        <span className="avatar">
                            {initials(student)}
                        </span>
                        <div>
                            <strong>{student.name}</strong>
                            <small>
                                {student.studentId} · {student.email}
                            </small>
                        </div>
                        {role === "teacher" && (
                            <span>
                                {
                                    enrollments.filter(
                                        (enrollment) =>
                                            enrollment.studentId ===
                                            student.studentId
                                    ).length
                                }{" "}
                                courses
                            </span>
                        )}
                    </div>
                ))}

                {!filtered.length && (
                    <Empty text="No students match your search." />
                )}
            </div>
        </>
    );
}

function TeachersPage({ teachers, courses }) {
    return (
        <>
            <PageHeader
                eyebrow="Teachers"
                title="Teacher directory"
                description="Teacher accounts and the courses they manage."
            />

            <div className="list">
                {teachers.map((teacher) => {
                    const taughtCourses = courses.filter(
                        (course) =>
                            course.teacherId === teacher.teacher_id
                    );

                    return (
                        <div className="list-row" key={teacher.teacher_id}>
                            <span className="avatar">
                                {initials(teacher)}
                            </span>
                            <div>
                                <strong>{teacher.teacher_name}</strong>
                                <small>
                                    {teacher.teacher_id} · {teacher.teacher_email}
                                </small>
                            </div>
                            <span>
                                {taughtCourses.length
                                    ? taughtCourses
                                          .map((course) => course.courseName)
                                          .join(", ")
                                    : "No courses assigned"}
                            </span>
                        </div>
                    );
                })}
            </div>
        </>
    );
}

function RightsPage({ rights, students }) {
    return (
        <>
            <PageHeader
                eyebrow="Study rights"
                title="Study rights"
                description="Study-right records derived from mock enrolments."
            />

            <div className="list">
                {rights.map((right) => {
                    const student = students.find(
                        (item) => item.studentId === right.studentId
                    );

                    return (
                        <div
                            className="list-row"
                            key={right.studyRightId}
                        >
                            <span className="avatar">
                                {initials(student || {})}
                            </span>
                            <div>
                                <strong>
                                    {student?.name || right.studentId}
                                </strong>
                                <small>{right.courseName}</small>
                            </div>
                            <span className="pill">
                                {right.status}
                            </span>
                        </div>
                    );
                })}
            </div>
        </>
    );
}

function CourseCard({ course, large = false }) {
    return (
        <div className={`course-card ${large ? "large" : ""}`}>
            <div className="course-banner">
                {course.courseCode || course.courseId}
            </div>
            <div className="course-body">
                <span className="eyebrow">
                    {course.teacherName || "Course"}
                </span>
                <h2>{course.courseName}</h2>
                <p>
                    {course.description ||
                        "Course information from the mock learning environment."}
                </p>
                {course.courseUrl && (
                    <span className="course-link">
                        Course link →
                    </span>
                )}
            </div>
        </div>
    );
}

function Nav({ active, onClick, icon, children }) {
    return (
        <button
            className={`nav-item ${active ? "active" : ""}`}
            type="button"
            onClick={onClick}
        >
            <span>{icon}</span>
            {children}
        </button>
    );
}

function PageHeader({ eyebrow, title, description }) {
    return (
        <div className="page-header">
            <span className="eyebrow">{eyebrow}</span>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
    );
}

function Header({ title, subtitle }) {
    return (
        <div className="panel-header">
            <div>
                <h2>{title}</h2>
                {subtitle && <p>{subtitle}</p>}
            </div>
        </div>
    );
}

function Stat({ icon, value, label }) {
    return (
        <div className="stat-card">
            <div className="stat-icon">{icon}</div>
            <strong>{value}</strong>
            <span>{label}</span>
        </div>
    );
}

function Info({ label, value }) {
    return (
        <div className="info-row">
            <span>{label}</span>
            <strong>{value || "—"}</strong>
        </div>
    );
}

function Record({ title, value }) {
    return (
        <div className="record">
            <strong>{title || "Study right"}</strong>
            <span>{value || "Active"}</span>
        </div>
    );
}

function Empty({ text }) {
    return <div className="empty">{text}</div>;
}

function Loading({ error, onRetry }) {
    return (
        <div className="loading-screen">
            <div className="loading-logo">{error ? "!" : "P"}</div>
            <h2>
                {error ? "PeppiMock unavailable" : "Loading PeppiMock..."}
            </h2>
            <p>
                {error ||
                    "Connecting to the mock student information system."}
            </p>
            {error && onRetry && (
                <button
                    className="primary-button compact"
                    type="button"
                    onClick={onRetry}
                >
                    Retry
                </button>
            )}
        </div>
    );
}

function nameOf(value) {
    return (
        value?.name ||
        value?.teacher_name ||
        value?.teacherName ||
        "Administrator"
    );
}

function firstName(value) {
    return nameOf(value).split(" ")[0];
}

function initials(value) {
    const parts = nameOf(value).split(" ").filter(Boolean);
    return `${parts[0]?.[0] || ""}${parts[1]?.[0] || ""}`.toUpperCase();
}

function averageProgress(students) {
    if (!students.length) return 0;
    return Math.round(
        students.reduce(
            (sum, student) => sum + (student.progressPercentage || 0),
            0
        ) / students.length
    );
}

export default App;
