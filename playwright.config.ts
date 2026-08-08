import { defineConfig } from "@playwright/test";

export default defineConfig({
    testDir: "./tests",

    // These tests modify shared JSON files, so they must not run in parallel.
    fullyParallel: false,
    workers: 1,

    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,

    reporter: "html",

    use: {
        trace: "on-first-retry"
    },

    // The project tests a Python/JSON workflow, not a browser UI.
    // Chromium is used only as the Playwright test runner.
    projects: [
        {
            name: "chromium",
            use: {
                browserName: "chromium"
            }
        }
    ]
});
