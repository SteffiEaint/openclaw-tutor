import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8002";

function App() {
    const [data, setData] = useState(null);
    const [session, setSession] = useState(null);
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const [loginLoading, setLoginLoading] = useState(false);
    const [page, setPage] = useState("inbox");
    const [selectedMessage, setSelectedMessage] = useState(null);
    const [composeOpen, setComposeOpen] = useState(false);
    const [composeForm, setComposeForm] = useState({
        to: "",
        subject: "",
        body: "",
    });
    const [sending, setSending] = useState(false);

    useEffect(() => {
        let active = true;

        async function initialize() {
            try {
                const result = await fetchData();
                if (!active) return;

                setData(result);

                const saved = localStorage.getItem("mailermock_session");
                if (saved) {
                    try {
                        const savedSession = JSON.parse(saved);
                        const validUser = (result.users || []).some(
                            (user) =>
                                normalizeEmail(user.email) ===
                                normalizeEmail(savedSession.email)
                        );

                        if (validUser) {
                            setSession(savedSession);
                        } else {
                            localStorage.removeItem("mailermock_session");
                        }
                    } catch {
                        localStorage.removeItem("mailermock_session");
                    }
                }
            } catch (err) {
                console.error(err);
                if (active) {
                    setError(
                        err.message ||
                            "Unable to connect to MailerMock."
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
                "MailerMock is unavailable. Start the MailerMock server and refresh."
            );
        }

        return response.json();
    }

    async function refreshData() {
        try {
            const result = await fetchData();
            setData(result);
            setError("");
            return result;
        } catch (err) {
            console.error(err);
            setError(err.message || "Unable to refresh MailerMock.");
            return null;
        }
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
                    result.error || "MailerMock login failed."
                );
            }

            setSession(result.user);
            localStorage.setItem(
                "mailermock_session",
                JSON.stringify(result.user)
            );
            setPassword("");
            setPage("inbox");
        } catch (err) {
            console.error(err);
            setError(err.message || "Unable to log in.");
        } finally {
            setLoginLoading(false);
        }
    }

    function logout() {
        localStorage.removeItem("mailermock_session");
        setSession(null);
        setSelectedMessage(null);
        setComposeOpen(false);
        setComposeForm({ to: "", subject: "", body: "" });
        setEmail("");
        setPassword("");
        setPage("inbox");
    }

    async function openMessage(message) {
        setSelectedMessage(message);
        setPage("message");

        if (message.read) return;

        try {
            const response = await fetch(
                `${API}/api/read/${encodeURIComponent(message.id)}`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({}),
                }
            );

            if (!response.ok) return;

            const result = await response.json();
            setSelectedMessage(result.message || { ...message, read: true });
            await refreshData();
        } catch (err) {
            console.error(err);
        }
    }

    function openCompose(recipient = "") {
        setComposeForm({
            to: recipient,
            subject: "",
            body: "",
        });
        setComposeOpen(true);
        setError("");
    }

    function replyToMessage(message) {
        const senderIsCurrentUser =
            normalizeEmail(message.from) ===
            normalizeEmail(session.email);

        setComposeForm({
            to: senderIsCurrentUser ? message.to : message.from,
            subject: message.subject?.startsWith("Re:")
                ? message.subject
                : `Re: ${message.subject || "(No subject)"}`,
            body: `\n\n--- Original message ---\n${message.body || ""}`,
        });
        setComposeOpen(true);
    }

    async function sendMessage(event) {
        event.preventDefault();
        setSending(true);
        setError("");

        try {
            const response = await fetch(`${API}/api/send`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    from: session.email,
                    to: composeForm.to.trim(),
                    subject: composeForm.subject.trim(),
                    body: composeForm.body,
                }),
            });

            const result = await response.json();

            if (!response.ok || !result.success) {
                throw new Error(
                    result.error || "Could not send message."
                );
            }

            setComposeOpen(false);
            setComposeForm({ to: "", subject: "", body: "" });
            setPage("sent");
            await refreshData();
        } catch (err) {
            console.error(err);
            setError(err.message || "Could not send message.");
        } finally {
            setSending(false);
        }
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

    if (!session) {
        return (
            <LoginPage
                email={email}
                password={password}
                setEmail={setEmail}
                setPassword={setPassword}
                error={error}
                loading={loginLoading}
                onLogin={handleLogin}
                users={data.users || []}
            />
        );
    }

    const currentEmail = normalizeEmail(session.email);
    const messages = data.messages || [];
    const users = data.users || [];

    const inbox = messages
        .filter((message) => normalizeEmail(message.to) === currentEmail)
        .sort(sortNewest);

    const sent = messages
        .filter((message) => normalizeEmail(message.from) === currentEmail)
        .sort(sortNewest);

    const unread = inbox.filter((message) => !message.read).length;

    let content;

    if (page === "message" && selectedMessage) {
        content = (
            <MessageView
                message={selectedMessage}
                onBack={() => {
                    const sentByCurrentUser =
                        normalizeEmail(selectedMessage.from) === currentEmail;
                    setPage(sentByCurrentUser ? "sent" : "inbox");
                }}
                onReply={() => replyToMessage(selectedMessage)}
            />
        );
    } else if (page === "contacts") {
        content = (
            <Contacts
                users={users}
                onCompose={openCompose}
            />
        );
    } else if (page === "about") {
        content = <About />;
    } else {
        const showingSent = page === "sent";
        content = (
            <Mailbox
                title={showingSent ? "Sent" : "Inbox"}
                subtitle={
                    showingSent
                        ? "Messages you have sent."
                        : `${unread} unread message${unread === 1 ? "" : "s"}`
                }
                messages={showingSent ? sent : inbox}
                onMessage={openMessage}
                onRefresh={refreshData}
            />
        );
    }

    return (
        <div className="app">
            <header className="topbar">
                <button
                    className="brand"
                    type="button"
                    onClick={() => {
                        setSelectedMessage(null);
                        setPage("inbox");
                    }}
                >
                    <span className="brand-mark">✉</span>
                    <span>
                        <strong>MailerMock</strong>
                        <small>Mock email service</small>
                    </span>
                </button>

                <div className="topbar-right">
                    <span className="account-role">
                        {session.role}
                    </span>
                    <button
                        className="account"
                        type="button"
                        onClick={logout}
                        title="Sign out"
                    >
                        <span className="avatar">
                            {initials(session.name)}
                        </span>
                        <span>{session.name}</span>
                        <span>↪</span>
                    </button>
                </div>
            </header>

            <div className="mail-layout">
                <aside className="mail-sidebar">
                    <button
                        className="compose-button"
                        type="button"
                        onClick={() => openCompose()}
                    >
                        ＋ Compose
                    </button>

                    <nav>
                        <MailNav
                            active={page === "inbox"}
                            onClick={() => {
                                setSelectedMessage(null);
                                setPage("inbox");
                            }}
                            icon="▣"
                            count={unread}
                        >
                            Inbox
                        </MailNav>
                        <MailNav
                            active={page === "sent"}
                            onClick={() => {
                                setSelectedMessage(null);
                                setPage("sent");
                            }}
                            icon="➤"
                        >
                            Sent
                        </MailNav>
                        <MailNav
                            active={page === "contacts"}
                            onClick={() => {
                                setSelectedMessage(null);
                                setPage("contacts");
                            }}
                            icon="♙"
                        >
                            Contacts
                        </MailNav>
                        <MailNav
                            active={page === "about"}
                            onClick={() => {
                                setSelectedMessage(null);
                                setPage("about");
                            }}
                            icon="ⓘ"
                        >
                            MailerMock info
                        </MailNav>
                    </nav>

                    <div className="mail-sidebar-footer">
                        <span>{session.email}</span>
                        <button type="button" onClick={logout}>
                            Sign out
                        </button>
                    </div>
                </aside>

                <main className="mail-main">
                    {error && (
                        <div className="global-error">
                            {error}
                        </div>
                    )}
                    {content}
                </main>
            </div>

            {composeOpen && (
                <ComposeModal
                    form={composeForm}
                    setForm={setComposeForm}
                    recipients={users}
                    sending={sending}
                    error={error}
                    onClose={() => setComposeOpen(false)}
                    onSend={sendMessage}
                />
            )}
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
    users,
}) {
    return (
        <div className="login-screen">
            <div className="login-card">
                <div className="login-logo">✉</div>
                <h1>MailerMock</h1>
                <p>Sign in to your mock email account.</p>

                <form onSubmit={onLogin}>
                    <label htmlFor="mailer-email">Email address</label>
                    <input
                        id="mailer-email"
                        type="email"
                        value={email}
                        onChange={(event) => setEmail(event.target.value)}
                        placeholder="student@example.com"
                        required
                    />

                    <label htmlFor="mailer-password">Password</label>
                    <input
                        id="mailer-password"
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
                    <strong>Available accounts</strong>
                    <p>
                        Any student or teacher email from the mock
                        environment can be used. Passwords are intentionally
                        not validated in this prototype.
                    </p>
                    <div>
                        {users.slice(0, 8).map((user) => (
                            <button
                                key={user.email}
                                type="button"
                                onClick={() => setEmail(user.email)}
                            >
                                {user.email}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

function Mailbox({ title, subtitle, messages, onMessage, onRefresh }) {
    return (
        <>
            <div className="page-header">
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                </div>
                <button
                    className="refresh-button"
                    type="button"
                    onClick={onRefresh}
                >
                    ↻ Refresh
                </button>
            </div>

            <div className="message-list">
                {messages.map((message) => (
                    <button
                        className={`message-row ${message.read ? "" : "unread"}`}
                        type="button"
                        key={message.id}
                        onClick={() => onMessage(message)}
                    >
                        <span className="sender-avatar">
                            {initials(message.fromName || message.from)}
                        </span>
                        <div className="message-main">
                            <strong>
                                {message.fromName || message.from}
                            </strong>
                            <span>
                                {message.subject || "(No subject)"}
                            </span>
                            <small>{truncate(message.body, 90)}</small>
                        </div>
                        <time>{formatDate(message.createdAt)}</time>
                    </button>
                ))}

                {!messages.length && (
                    <div className="empty">No messages here yet.</div>
                )}
            </div>
        </>
    );
}

function MessageView({ message, onBack, onReply }) {
    return (
        <div className="message-view">
            <button className="back-button" type="button" onClick={onBack}>
                ← Back
            </button>

            <div className="message-card">
                <div className="message-header">
                    <div>
                        <h1>{message.subject || "(No subject)"}</h1>
                        <div className="meta">
                            <strong>
                                {message.fromName || message.from}
                            </strong>{" "}
                            &lt;{message.from}&gt; → &lt;{message.to}&gt;
                        </div>
                    </div>
                    <span>{formatDateTime(message.createdAt)}</span>
                </div>

                <div className="message-body">{message.body}</div>

                <div className="message-actions">
                    <button
                        className="primary-button small-button"
                        type="button"
                        onClick={onReply}
                    >
                        Reply
                    </button>
                </div>
            </div>
        </div>
    );
}

function Contacts({ users, onCompose }) {
    return (
        <>
            <div className="page-header">
                <div>
                    <h1>Contacts</h1>
                    <p>
                        Students and teachers available in the mock
                        environment.
                    </p>
                </div>
            </div>

            <div className="contacts-grid">
                {users.map((user) => (
                    <div className="contact-card" key={user.email}>
                        <span className="avatar">{initials(user.name)}</span>
                        <div>
                            <strong>{user.name}</strong>
                            <small>{user.role}</small>
                            <span>{user.email}</span>
                        </div>
                        <button
                            type="button"
                            onClick={() => onCompose(user.email)}
                        >
                            Email
                        </button>
                    </div>
                ))}
            </div>
        </>
    );
}

function About() {
    return (
        <div className="about-card">
            <div className="brand-mark large">✉</div>
            <h1>MailerMock</h1>
            <p>
                A lightweight mock email service used by the OpenClaw Tutor
                workflow.
            </p>
            <ul>
                <li>Student and teacher sign-in</li>
                <li>Separate inbox and sent mail</li>
                <li>User-to-user messages</li>
                <li>OpenClaw-generated emails appear in inboxes</li>
                <li>Messages are stored locally in JSON</li>
            </ul>
        </div>
    );
}

function ComposeModal({
    form,
    setForm,
    recipients,
    sending,
    error,
    onClose,
    onSend,
}) {
    return (
        <div className="modal-backdrop">
            <form className="compose-modal" onSubmit={onSend}>
                <div className="modal-header">
                    <strong>New message</strong>
                    <button type="button" onClick={onClose}>
                        ×
                    </button>
                </div>

                <label htmlFor="compose-to">To</label>
                <input
                    id="compose-to"
                    list="mailer-recipients"
                    value={form.to}
                    onChange={(event) =>
                        setForm({ ...form, to: event.target.value })
                    }
                    placeholder="recipient@example.com"
                    required
                />
                <datalist id="mailer-recipients">
                    {recipients.map((recipient) => (
                        <option
                            key={recipient.email}
                            value={recipient.email}
                        >
                            {recipient.name}
                        </option>
                    ))}
                </datalist>

                <label htmlFor="compose-subject">Subject</label>
                <input
                    id="compose-subject"
                    value={form.subject}
                    onChange={(event) =>
                        setForm({ ...form, subject: event.target.value })
                    }
                    placeholder="Subject"
                />

                <label htmlFor="compose-body">Message</label>
                <textarea
                    id="compose-body"
                    value={form.body}
                    onChange={(event) =>
                        setForm({ ...form, body: event.target.value })
                    }
                    rows="12"
                    placeholder="Write your message..."
                    required
                />

                {error && <div className="login-error">{error}</div>}

                <div className="modal-actions">
                    <button type="button" onClick={onClose}>
                        Cancel
                    </button>
                    <button
                        className="primary-button"
                        type="submit"
                        disabled={sending}
                    >
                        {sending ? "Sending..." : "Send"}
                    </button>
                </div>
            </form>
        </div>
    );
}

function MailNav({ active, onClick, icon, count, children }) {
    return (
        <button
            className={`mail-nav ${active ? "active" : ""}`}
            type="button"
            onClick={onClick}
        >
            <span>{icon}</span>
            {children}
            {count > 0 && <b>{count}</b>}
        </button>
    );
}

function Loading({ error, onRetry }) {
    return (
        <div className="loading-screen">
            <div className="loading-logo">{error ? "!" : "✉"}</div>
            <h2>{error ? "MailerMock unavailable" : "Loading MailerMock..."}</h2>
            <p>
                {error || "Connecting to the mock email service."}
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

function normalizeEmail(value) {
    return String(value || "").trim().toLowerCase();
}

function initials(name = "") {
    const parts = String(name).split(" ").filter(Boolean);
    return `${parts[0]?.[0] || ""}${parts[1]?.[0] || ""}`.toUpperCase();
}

function sortNewest(a, b) {
    return new Date(b.createdAt || 0) - new Date(a.createdAt || 0);
}

function truncate(value = "", length = 90) {
    const text = String(value);
    return text.length > length ? `${text.slice(0, length)}…` : text;
}

function formatDate(value) {
    if (!value) return "";
    return new Date(value).toLocaleDateString("en-GB", {
        day: "numeric",
        month: "short",
    });
}

function formatDateTime(value) {
    if (!value) return "";
    return new Date(value).toLocaleString("en-GB", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

export default App;
