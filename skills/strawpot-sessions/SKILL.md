---
name: strawpot-sessions
description: Inspect StrawPot session traces, logs, and artifacts
metadata:
  strawpot:
---

# StrawPot Session Inspection

## Session Storage

Sessions are stored at `<project>/.strawpot/sessions/<run_id>/`.
Bot Imu sessions are stored at `~/.strawpot/.strawpot/sessions/<run_id>/`
(Bot Imu uses `~/.strawpot` as its working directory).

## Find Sessions

```bash
# Active sessions for a project
ls <project>/.strawpot/running/

# Archived sessions
ls <project>/.strawpot/archive/

# All sessions
ls <project>/.strawpot/sessions/
## Read Session Metadata

```bash
cat <project>/.strawpot/sessions/<run_id>/session.json | python3 -m json.tool
```

Key fields: `run_id`, `working_dir`, `role`, `runtime`, `isolation`,
`started_at`, `pid`, `task`, `agents` (map of agent_id → agent info).

## Read Trace Events

```bash
# All events
cat <project>/.strawpot/sessions/<run_id>/trace.jsonl | python3 -m json.tool --json-lines

# Filter by event type
grep '"event": "delegate_start"' <project>/.strawpot/sessions/<run_id>/trace.jsonl
```

Event types: `session_start`, `session_end`, `delegate_start`,
`delegate_end`, `delegate_denied`, `agent_spawn`, `agent_end`,
`memory_get`, `memory_dump`, `memory_remember`.

## Read Agent Logs

```bash
cat <project>/.strawpot/sessions/<run_id>/agents/<agent_id>/.log
```

## Read Artifacts

Fields ending in `_ref` (e.g., `context_ref`, `output_ref`) are
SHA256[:12] hashes. Read the artifact:

```bash
cat <project>/.strawpot/sessions/<run_id>/artifacts/<hash>
```

## Via GUI API

```bash
# List sessions for a project
curl -s http://127.0.0.1:8741/api/projects/{id}/sessions | python3 -m json.tool

# Session detail with agents and events
curl -s http://127.0.0.1:8741/api/projects/{id}/sessions/{run_id} | python3 -m json.tool

# Read artifact
curl -s http://127.0.0.1:8741/api/sessions/{run_id}/artifacts/{hash}
```
```
