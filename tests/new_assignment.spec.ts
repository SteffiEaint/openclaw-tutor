import { test, expect } from "@playwright/test";

import {
    ASSIGNMENTS,
    ASSIGNMENT_SNAPSHOT,
    COMPLETIONS,
    COMPLETION_SNAPSHOT,
    EVENTS,
    NOTIFICATION_QUEUE,
    loadJson,
    saveJson,
    backup,
    restore,
    runWorkflow
} from "./helpers";

test("Publishing a new assignment creates records and notifications", () => {
    const originalAssignments = backup(ASSIGNMENTS);
    const originalCompletions = backup(COMPLETIONS);
    const originalAssignmentSnapshot = backup(ASSIGNMENT_SNAPSHOT);
    const originalCompletionSnapshot = backup(COMPLETION_SNAPSHOT);
    const originalEvents = backup(EVENTS);
    const originalNotifications = backup(NOTIFICATION_QUEUE);

    try {
        saveJson(EVENTS, []);
        saveJson(NOTIFICATION_QUEUE, []);

        const assignments = loadJson(ASSIGNMENTS);

        assignments.push({
            assignmentId: "ATEST",
            courseId: "C101",
            title: "Playwright Test Assignment",
            description: "Testing",
            dueDate: "2030-12-31T23:59:59Z"
        });

        saveJson(ASSIGNMENTS, assignments);

        // Make ATEST look newly published.
        const snapshot = loadJson(ASSIGNMENT_SNAPSHOT).filter(
            (assignment: any) =>
                assignment.assignmentId !== "ATEST"
        );

        saveJson(ASSIGNMENT_SNAPSHOT, snapshot);

        runWorkflow();

        const events = loadJson(EVENTS);

        expect(
            events.some(
                (event: any) =>
                    event.event === "new_assignment" &&
                    event.assignmentId === "ATEST"
            )
        ).toBeTruthy();

        const completions = loadJson(COMPLETIONS);

        expect(
            completions.some(
                (completion: any) =>
                    completion.assignmentId === "ATEST"
            )
        ).toBeTruthy();

        const queue = loadJson(NOTIFICATION_QUEUE);

        expect(
            queue.some(
                (notification: any) =>
                    notification.notification_type === "new_assignment" &&
                    notification.assignment_id === "ATEST"
            )
        ).toBeTruthy();
    } finally {
        restore(ASSIGNMENTS, originalAssignments);
        restore(COMPLETIONS, originalCompletions);
        restore(ASSIGNMENT_SNAPSHOT, originalAssignmentSnapshot);
        restore(COMPLETION_SNAPSHOT, originalCompletionSnapshot);
        restore(EVENTS, originalEvents);
        restore(NOTIFICATION_QUEUE, originalNotifications);
    }
});
