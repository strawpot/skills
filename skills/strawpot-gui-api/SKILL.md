---
name: strawpot-gui-api
description: StrawPot GUI REST API — projects, sessions, resources
metadata:
  strawpot:
    tools:
      curl:
        description: HTTP client for GUI API calls
        install:
          linux: apt install curl
---

# StrawPot GUI REST API

The GUI exposes a REST API at `http://127.0.0.1:8741/api`.
Use this when the GUI is running — it is safer and returns structured
JSON rather than requiring filesystem access.

## Check if GUI is Running

```bash
curl -s http://127.0.0.1:8741/api/health
If not running, start it: `strawpot gui --port 8741 &`

## Projects

```bash
# List all registered projects
curl -s http://127.0.0.1:8741/api/projects | python3 -m json.tool

# Get a specific project (with session count, resources)
curl -s http://127.0.0.1:8741/api/projects/{id} | python3 -m json.tool
```

Key fields: `id`, `name`, `directory`, `session_count`,
`active_session_count`, `installed_roles`, `installed_skills`.

## Sessions

```bash
# List sessions for a project (newest first, paginated)
curl -s "http://127.0.0.1:8741/api/projects/{id}/sessions?limit=10" | python3 -m json.tool

# Get session detail (status, agents, trace events, tree)
curl -s http://127.0.0.1:8741/api/projects/{id}/sessions/{run_id} | python3 -m json.tool

# Launch a new session
curl -s -X POST http://127.0.0.1:8741/api/projects/{id}/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "task": "implement feature X",
    "role": "implementer",
    "interactive": false
  }' | python3 -m json.tool

# Stop a running session
curl -s -X POST http://127.0.0.1:8741/api/projects/{id}/sessions/{run_id}/stop

# Read an artifact by hash
curl -s http://127.0.0.1:8741/api/sessions/{run_id}/artifacts/{hash}
```

Session status values: `starting`, `running`, `completed`, `failed`, `stopped`.

## Installed Resources

```bash
# List globally installed roles
curl -s http://127.0.0.1:8741/api/registry/roles | python3 -m json.tool

# List globally installed skills
curl -s http://127.0.0.1:8741/api/registry/skills | python3 -m json.tool

# List project-scoped resources
curl -s http://127.0.0.1:8741/api/projects/{id}/resources | python3 -m json.tool

# Install a resource to a project
curl -s -X POST http://127.0.0.1:8741/api/projects/{id}/resources \
  -H "Content-Type: application/json" \
  -d '{"type": "skill", "name": "git-workflow"}' | python3 -m json.tool

# Remove a resource from a project
curl -s -X DELETE http://127.0.0.1:8741/api/projects/{id}/resources/{type}/{name}
```

## Configuration

```bash
# Get project config
curl -s http://127.0.0.1:8741/api/projects/{id}/config | python3 -m json.tool

# Update a config key (PATCH merges, does not overwrite)
curl -s -X PATCH http://127.0.0.1:8741/api/projects/{id}/config \
  -H "Content-Type: application/json" \
  -d '{"runtime": "strawpot-codex", "max_depth": 4}'

# Get global config
curl -s http://127.0.0.1:8741/api/config | python3 -m json.tool
```
```
