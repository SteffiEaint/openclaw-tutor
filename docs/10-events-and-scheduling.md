# Events, Triggers, and Scheduling

## Why an event layer exists

Mock JSON data is static until something changes it. The system therefore uses snapshots to detect changes between workflow runs.

## Snapshot files

- `events/assignment_snapshot.json`
- `events/completion_snapshot.json`

## Event types

The event engine can detect conditions including:

- `new_assignment`;
- `completion_created`;
- `assignment_missing`;
- `assignment_completed`;
- late/submission-related state changes where applicable in the event engine.

## New assignment detection

The engine compares assignment IDs in the current `assignments.json` against the previous assignment snapshot. A new ID creates a `new_assignment` event.

## Completion record creation

For every enrollment and course assignment, the event engine can create a missing completion record with an initial `in-progress` status.

This means the system can derive completion state for newly created assignments without manually editing every student's completion file.

## Due-date detection

An `in-progress` completion becomes `missing` when its assignment due date has passed and it has not been completed.

## Completion detection

The engine compares the current completion snapshot with the previous state. A transition from a non-completed state to `completed` can generate an `assignment_completed` event.

## Trigger configuration

`config/triggers.json` contains example trigger definitions for:

- scheduled runs;
- progress updates;
- manual actions;
- new assignments.

The trigger definitions describe the intended event sources; they are not a substitute for the event engine itself.

## Scheduler

`scheduler/scheduler.py` uses the Python `schedule` package to execute `run_full_workflow()` according to configuration.

Supported current modes include interval-based scheduling and daily scheduling.

## Important limitation

The scheduler does not make the JSON data itself event-driven. It periodically runs the workflow, and the event engine compares current state with snapshots.

This is a deliberate prototype simplification.
