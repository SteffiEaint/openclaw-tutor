import { test, expect } from "@playwright/test";

import {
    loadJson,
    saveJson,
    runWorkflow,
    COMPLETIONS,
    COMPLETION_SNAPSHOT,
    ASSIGNMENT_SNAPSHOT,
    ASSIGNMENTS,
    EVENTS,
    NOTIFICATION_QUEUE,
    EMAILS,
    backup,
    restore
} from "./helpers";

test("completed assignment creates completion event, notification and email", () => {
    const originalAssignments = backup(ASSIGNMENTS);
    const originalCompletions = backup(COMPLETIONS);
    const originalAssignmentSnapshot = backup(ASSIGNMENT_SNAPSHOT);
    const originalCompletionSnapshot = backup(COMPLETION_SNAPSHOT);
    const originalEvents = backup(EVENTS);
    const originalNotifications = backup(NOTIFICATION_QUEUE);
    const originalEmails = backup(EMAILS);

    try {
        saveJson(EVENTS, []);
        saveJson(NOTIFICATION_QUEUE, []);
        saveJson(EMAILS, []);

        const completions = loadJson(COMPLETIONS);

        const completion = completions.find(
            (item: any) =>
                item.studentId === "S001" &&
                item.assignmentId === "A003"
        );

        expect(completion).toBeDefined();

        completion.status = "completed";
        completion.submittedAt = "2026-08-05T10:00:00Z";

        saveJson(COMPLETIONS, completions);

        runWorkflow();

        const events = loadJson(EVENTS);

        expect(
            events.some(
                (event: any) =>
                    event.event === "assignment_completed" &&
                    event.studentId === "S001" &&
                    event.assignmentId === "A003"
            )
        ).toBeTruthy();

        const notifications = loadJson(NOTIFICATION_QUEUE);

        expect(
            notifications.some(
                (notification: any) =>
                    notification.notification_type === "assignment_completed" &&
                    notification.student_id === "S001" &&
                    notification.assignment_id === "A003"
            )
        ).toBeTruthy();

        const emails = loadJson(EMAILS);

        expect(
            emails.student_emails.some(
                (email: any) =>
                    email.type === "student_notification" &&
                    email.to === "alice.smith@example.com" &&
                    email.subject.includes("Assignment Completed")
            )
        ).toBeTruthy();
    } finally {
        restore(ASSIGNMENTS, originalAssignments);
        restore(COMPLETIONS, originalCompletions);
        restore(ASSIGNMENT_SNAPSHOT, originalAssignmentSnapshot);
        restore(COMPLETION_SNAPSHOT, originalCompletionSnapshot);
        restore(EVENTS, originalEvents);
        restore(NOTIFICATION_QUEUE, originalNotifications);
        restore(EMAILS, originalEmails);
    }
});
