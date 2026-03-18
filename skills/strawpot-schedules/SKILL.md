---
name: strawpot-schedules
description: Manage StrawPot scheduled tasks — both recurring (cron) and one-time schedules. Use this skill whenever the user wants to create, list, update, enable, disable, or delete scheduled tasks in StrawPot, whether they need something to run on a repeating cron schedule or fire once at a specific time.
metadata:
  strawpot:
    tools:
      curl:
        description: HTTP client for GUI API calls
        install:
          linux: apt install curl
---

# StrawPot Scheduled Tasks

StrawPot supports two types of scheduled tasks that automatically launch agent sessions:

- **Recurring schedules** — run on a cron expression (e.g., every weekday at 9am)
- **One-time schedules** — run once at a specific datetime, then auto-disable

Both types are managed through the GUI API. The scheduler checks every 30 seconds for schedules where `next_run_at <= now` and launches headless sessions. The scheduler only runs while the GUI server is running — missed executions are not retried retroactively.

## API Base

```
http://127.0.0.1:8741/api
```

Check if GUI is running:

```bash
curl -s http://127.0.0.1:8741/api/health
```

If not running, start it with `strawpot gui --port 8741`.

---

## Creating Schedules

### Recurring Schedule (Cron)

```bash
curl -s -X POST http://127.0.0.1:8741/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "daily-github-triage",
    "project_id": 1,
    "task": "Review open GitHub issues and PRs, triage by priority",
    "cron_expr": "0 9 * * 1-5",
    "role": "github-triage"
  }'
```

Recurring schedules are created disabled. Call the enable endpoint after creation.

### One-Time Schedule

```bash
curl -s -X POST http://127.0.0.1:8741/api/schedules/one-time \
  -H "Content-Type: application/json" \
  -d '{
    "name": "deploy-tonight",
    "project_id": 1,
    "task": "Deploy to staging and run smoke tests",
    "run_at": "2026-03-15T02:00:00+00:00"
  }'
```

The `run_at` field must be an ISO 8601 datetime set in the future. The system copies `run_at` into `next_run_at` at creation.

**After firing**, a one-time schedule automatically:
1. Sets `enabled = 0`
2. Clears `next_run_at` to `NULL`

A fired one-time schedule **cannot be re-enabled** — create a new schedule instead.

---

## List Schedules

```bash
# All schedules
curl -s http://127.0.0.1:8741/api/schedules | python3 -m json.tool

# Filter by type
curl -s "http://127.0.0.1:8741/api/schedules?type=recurring" | python3 -m json.tool
curl -s "http://127.0.0.1:8741/api/schedules?type=one_time" | python3 -m json.tool
```

## View Schedule Runs

Lists all sessions triggered by schedules (both types), with pagination:

```bash
curl -s "http://127.0.0.1:8741/api/schedules/runs?page=1&per_page=20" | python3 -m json.tool
```

Each run includes `schedule_name`, `schedule_type`, `project_name`, `status`, `started_at`, and `duration_ms`.

## View History for a Specific Schedule

```bash
curl -s http://127.0.0.1:8741/api/schedules/{id}/history | python3 -m json.tool
```

## Update a Schedule

```bash
curl -s -X PUT http://127.0.0.1:8741/api/schedules/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "cron_expr": "0 8 * * *",
    "task": "Updated task description"
  }'
```

For one-time schedules, you can update `run_at` instead of `cron_expr`. If the schedule is enabled and `run_at` is updated, `next_run_at` is also updated to match.

## Enable / Disable

```bash
curl -s -X POST http://127.0.0.1:8741/api/schedules/{id}/enable
curl -s -X POST http://127.0.0.1:8741/api/schedules/{id}/disable
```

For one-time schedules, enabling validates that `run_at` is still in the future — returns **422** if the time has passed.

## Delete a Schedule

```bash
curl -s -X DELETE http://127.0.0.1:8741/api/schedules/{id}
```

---

## Recurring vs. One-Time Comparison

| Aspect | Recurring | One-Time |
|--------|-----------|----------|
| **Endpoint** | `POST /api/schedules` | `POST /api/schedules/one-time` |
| **Trigger field** | `cron_expr` | `run_at` (ISO 8601 datetime) |
| **Repetition** | Fires on every cron tick | Fires once |
| **After firing** | Computes next cron run | Auto-disables (`enabled=0`, `next_run_at=NULL`) |
| **Re-enable** | Yes | Only if `run_at` is still in the future |
| **Skip if running** | Configurable (default: true) — advances to next tick | Always false — will fire regardless |

### One-Time Schedule Lifecycle States

- **Pending** — enabled, waiting for `run_at`
- **Fired** — executed and auto-disabled (cannot be re-enabled)
- **Disabled** — manually paused before execution

---

## Cron Expression Reference

For recurring schedules only:

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun=0)
│ │ │ │ │
* * * * *
```

Common patterns:
- `0 9 * * 1-5` — weekdays at 9am
- `*/30 * * * *` — every 30 minutes
- `0 0 * * 0` — weekly on Sunday midnight
- `0 */6 * * *` — every 6 hours

---

## Fields Reference

### Recurring Schedule Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Unique schedule name |
| `project_id` | integer | yes | Target project |
| `task` | string | yes | Task description for the agent |
| `cron_expr` | string | yes | Cron expression (validated) |
| `role` | string | no | Role override (uses project default if omitted) |
| `system_prompt` | string | no | Additional instructions appended to the role prompt |
| `skip_if_running` | boolean | no | Skip if a session from this schedule is already running (default: true) |

### One-Time Schedule Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Unique schedule name |
| `project_id` | integer | yes | Target project |
| `task` | string | yes | Task description for the agent |
| `run_at` | string | yes | ISO 8601 datetime — must be in the future |
| `role` | string | no | Role override (uses project default if omitted) |
| `system_prompt` | string | no | Additional instructions appended to the role prompt |

### Response Fields (Both Types)

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Schedule ID |
| `schedule_type` | string | `"recurring"` or `"one_time"` |
| `cron_expr` | string/null | Cron expression (null for one-time) |
| `run_at` | string/null | ISO datetime (null for recurring) |
| `next_run_at` | string/null | Next scheduled execution time |
| `enabled` | boolean | Whether the schedule is active |
| `last_run_at` | string/null | Timestamp of last execution |
| `last_error` | string/null | Error from last execution attempt |
| `skip_if_running` | boolean | Skip behavior flag |
