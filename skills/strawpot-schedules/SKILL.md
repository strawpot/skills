---
name: strawpot-schedules
description: Manage StrawPot scheduled tasks (cron jobs)
metadata:
  strawpot:
    tools:
      curl:
        description: HTTP client for GUI API calls
        install:
          linux: apt install curl
---

# StrawPot Scheduled Tasks

Scheduled tasks are cron-based jobs that automatically launch StrawPot
sessions. They are managed through the GUI API.

## API Base

```
http://127.0.0.1:8741/api
```

Check if GUI is running:

```bash
curl -s http://127.0.0.1:8741/api/health
```

If not running, start it with `strawpot gui --port 8741`.

## List Schedules

```bash
curl -s http://127.0.0.1:8741/api/schedules | python3 -m json.tool
```

## Create a Schedule

Schedules are created disabled. Call the enable endpoint after creation.

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

## Update a Schedule

```bash
curl -s -X PUT http://127.0.0.1:8741/api/schedules/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "cron_expr": "0 8 * * *",
    "task": "Updated task description"
  }'
```

## Enable / Disable

```bash
curl -s -X POST http://127.0.0.1:8741/api/schedules/{id}/enable
curl -s -X POST http://127.0.0.1:8741/api/schedules/{id}/disable
```

## Delete a Schedule

```bash
curl -s -X DELETE http://127.0.0.1:8741/api/schedules/{id}
```

## View Schedule History

```bash
curl -s http://127.0.0.1:8741/api/schedules/{id}/history | python3 -m json.tool
```

## Cron Expression Reference

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

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | yes | Unique schedule name |
| `project_id` | integer | yes | Target project |
| `task` | string | yes | Task description for the agent |
| `cron_expr` | string | yes | Cron expression (validated) |
| `role` | string | no | Role override (uses project default if omitted) |
| `system_prompt` | string | no | Custom system prompt |
| `skip_if_running` | boolean | no | Skip if a session from this schedule is already running (default: true) |
