import { test, expect } from "@playwright/test";

import {
    loadJson,
    saveJson,
    runWorkflow,
    ASSIGNMENTS,
    COMPLETIONS,
    ASSIGNMENT_SNAPSHOT,
    COMPLETION_SNAPSHOT,
    EVENTS,
    NOTIFICATION_QUEUE,
    EMAILS,
    backup,
    restore
} from "./helpers";

test("overdue assignment becomes missing and notifies the student", () => {
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

        const assignments = loadJson(ASSIGNMENTS);
        const assignment = assignments.find(
            (item: any) => item.assignmentId === "A003"
        );

        expect(assignment).toBeDefined();

        assignment.dueDate = "2025-01-01T00:00:00Z";
        saveJson(ASSIGNMENTS, assignments);

        const completions = loadJson(COMPLETIONS);
        const completion = completions.find(
            (item: any) =>
                item.studentId === "S001" &&
                item.assignmentId === "A003"
        );

        expect(completion).toBeDefined();

        completion.status = "in-progress";
        completion.submittedAt = null;
        saveJson(COMPLETIONS, completions);

        runWorkflow();

        const updatedCompletions = loadJson(COMPLETIONS);
        const updatedCompletion = updatedCompletions.find(
            (item: any) =>
                item.studentId === "S001" &&
                item.assignmentId === "A003"
        );

        expect(updatedCompletion.status).toBe("missing");
        expect(updatedCompletion.submittedAt).toBeNull();

        const events = loadJson(EVENTS);

        expect(
            events.some(
                (event: any) =>
                    event.event === "assignment_missing" &&
                    event.studentId === "S001" &&
                    event.assignmentId === "A003"
            )
        ).toBeTruthy();

        const notifications = loadJson(NOTIFICATION_QUEUE);

        expect(
            notifications.some(
                (notification: any) =>
                    notification.notification_type === "assignment_missing" &&
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
                    email.subject.includes("Assignment Missing")
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
