import { test, expect } from "@playwright/test";

import {
    runWorkflow,
    loadJson,
    restore,
    backup,
    EVENTS,
    COMPLETIONS,
    ASSIGNMENT_SNAPSHOT,
    COMPLETION_SNAPSHOT,
    NOTIFICATION_QUEUE,
    EMAILS
} from "./helpers";

test("Workflow runs successfully", () => {
    const originalCompletions = backup(COMPLETIONS);
    const originalAssignmentSnapshot = backup(ASSIGNMENT_SNAPSHOT);
    const originalCompletionSnapshot = backup(COMPLETION_SNAPSHOT);
    const originalEvents = backup(EVENTS);
    const originalNotifications = backup(NOTIFICATION_QUEUE);
    const originalEmails = backup(EMAILS);

    try {
        runWorkflow();

        const notifications = loadJson(NOTIFICATION_QUEUE);
        const events = loadJson(EVENTS);
        const emails = loadJson(EMAILS);

        expect(Array.isArray(notifications)).toBeTruthy();
        expect(Array.isArray(events)).toBeTruthy();
        expect(emails).toHaveProperty("student_emails");
        expect(emails).toHaveProperty("teacher_summary_emails");
    } finally {
        restore(COMPLETIONS, originalCompletions);
        restore(ASSIGNMENT_SNAPSHOT, originalAssignmentSnapshot);
        restore(COMPLETION_SNAPSHOT, originalCompletionSnapshot);
        restore(EVENTS, originalEvents);
        restore(NOTIFICATION_QUEUE, originalNotifications);
        restore(EMAILS, originalEmails);
    }
});
