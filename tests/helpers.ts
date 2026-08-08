import { execSync } from "child_process";
import fs from "fs";
import path from "path";

export const ROOT = path.resolve(__dirname, "..");

export const EVENTS = path.join(ROOT, "events", "events.json");

export const ASSIGNMENTS = path.join(
    ROOT,
    "mocks",
    "moodlemock",
    "assignments.json"
);

export const COMPLETIONS = path.join(
    ROOT,
    "mocks",
    "moodlemock",
    "assignmentCompletions.json"
);

export const ASSIGNMENT_SNAPSHOT = path.join(
    ROOT,
    "events",
    "assignment_snapshot.json"
);

export const COMPLETION_SNAPSHOT = path.join(
    ROOT,
    "events",
    "completion_snapshot.json"
);

export const NOTIFICATION_QUEUE = path.join(
    ROOT,
    "reports",
    "notification_queue.json"
);

export const EMAILS = path.join(
    ROOT,
    "reports",
    "generated_emails.json"
);

export function loadJson(file: string) {
    return JSON.parse(fs.readFileSync(file, "utf8"));
}

export function saveJson(file: string, data: any) {
    fs.writeFileSync(
        file,
        JSON.stringify(data, null, 4),
        "utf8"
    );
}

export function backup(file: string) {
    return structuredClone(loadJson(file));
}

export function restore(file: string, data: any) {
    saveJson(file, data);
}

export function runWorkflow() {
    execSync(
        "python3 scheduler/workflow.py",
        {
            cwd: ROOT,
            stdio: "inherit"
        }
    );
}

export function clearEvents() {
    saveJson(EVENTS, []);
}

export function clearNotifications() {
    saveJson(NOTIFICATION_QUEUE, []);
}
