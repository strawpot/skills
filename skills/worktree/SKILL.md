---
name: worktree
description: "Manage git worktrees for task-level code isolation. Use this skill whenever an agent needs to isolate code changes — creating worktrees for multi-file changes, risky refactors, or implementation sub-issues, and cleaning them up when work is done. Trigger when: starting implementation work that touches multiple files, working on shared code, executing ordered sub-issues, or managing existing worktrees."
metadata:
  strawpot:
    tools:
      git:
        description: Git CLI
        install:
          macos: brew install git
          linux: apt install git
      gh:
        description: GitHub CLI (for PR detection during merge)
        install:
          macos: brew install gh
          linux: apt install gh
---

# Worktree Management

Manage git worktrees for task-level code isolation. Worktrees let
agents work in isolated copies of the repo without affecting the main
working directory.

All commands use the bundled script at `scripts/worktree.py` and
output JSON for programmatic consumption.

## Commands

### `create` — Create a worktree

Creates a new git worktree with a dedicated branch, records metadata
in the project manifest, and returns the worktree path.

```bash
# Basic — creates worktree branching from current branch
python scripts/worktree.py create --name my-feature

# Branch from a specific base (for stacked branches)
python scripts/worktree.py create --name 568-2-merge --base feature/568-1-create-list

# Link to an issue for tracking
python scripts/worktree.py create --name fix-auth --issue 42
```

**Parameters:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | Yes | — | Worktree name, used in path and branch name |
| `--base` | No | Current branch | Base branch to create from (stacked branch support) |
| `--issue` | No | — | Issue number to link in metadata |

**What it does:**

1. Creates worktree at `.strawpot/worktrees/<name>/`
2. Creates branch `worktree/<name>` from the base
3. Records entry in `.strawpot/worktrees.json` manifest
4. Outputs JSON with the worktree path and branch name

**Output:**
```json
{
  "status": "created",
  "name": "my-feature",
  "path": ".strawpot/worktrees/my-feature",
  "branch": "worktree/my-feature",
  "base_branch": "main"
}
```

### `list` — List worktrees and their status

Reads the manifest and cross-references with `git worktree list` to
show all tracked worktrees and detect orphaned entries.

```bash
python scripts/worktree.py list
```

**Output:**
```json
{
  "worktrees": [
    {
      "name": "my-feature",
      "path": ".strawpot/worktrees/my-feature",
      "branch": "worktree/my-feature",
      "base_branch": "main",
      "issue": 42,
      "created_at": "2026-03-27T12:00:00Z",
      "status": "active"
    }
  ]
}
```

**Status values:**

| Status | Meaning |
|--------|---------|
| `active` | Worktree exists and is in use |
| `stale` | In manifest but worktree directory is missing |

## Worktree layout

```
project/
├── .strawpot/
│   ├── worktrees.json          # Manifest tracking all worktrees
│   └── worktrees/
│       ├── my-feature/         # Worktree directory
│       └── fix-auth/           # Another worktree
```

## When to use worktrees

**Use a worktree** when:
- Changes touch multiple files across modules
- Refactoring shared code that other features depend on
- The change is risky or experimental
- Working on a long-running task that may span sessions
- Executing ordered sub-issues (stacked branches)

**Work directly** (no worktree) when:
- Single-file edits (docs, config, small fixes)
- Changes are trivially reversible
- Quick one-off tasks
