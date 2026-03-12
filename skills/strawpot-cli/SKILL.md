---
name: strawpot-cli
description: StrawPot CLI commands for session management
metadata:
  strawpot:
    tools:
      strawpot:
        description: StrawPot CLI
        install:
          macos: pip install strawpot
          linux: pip install strawpot
---

# StrawPot CLI

## Launch a Session

```bash
# Interactive session on a project
strawpot start --working-dir /path/to/project

# Headless session with a task
strawpot start --working-dir /path/to/project --headless --task "implement feature X"

# Override role and runtime
strawpot start --working-dir /path/to/project --role implementer --runtime strawpot-codex

# With custom system prompt
strawpot start --working-dir /path/to/project --headless --task "fix bug" --system-prompt "Focus on test coverage"
## Stop a Session

**Preferred (when GUI is running):** Use the GUI API (see
`strawpot-gui-api` skill — `POST /api/projects/{id}/sessions/{run_id}/stop`).

**Fallback (no GUI):** Find the session PID from `session.json`:

```bash
kill <pid>
```

## Session Status

Check `.strawpot/running/` for active sessions and `.strawpot/sessions/<run_id>/session.json` for details.

## Recovery

Stale sessions (PID dead but still in running/) are cleaned up automatically on next `strawpot start`.
```
