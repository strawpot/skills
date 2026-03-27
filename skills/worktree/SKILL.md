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
agents work on separate branches simultaneously — each worktree shares
the same `.git` directory but has its own working tree and index.

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
  "base_branch": "main",
  "issue": null
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
      "created_at": "2026-03-27T12:00:00+00:00",
      "status": "active"
    }
  ]
}
```

### `merge` — Merge worktree changes back

Merges changes from the worktree branch back to the base directory
and cleans up. Behavior depends on whether a PR exists for the branch.

```bash
python scripts/worktree.py merge --name my-feature
```

**Parameters:**

| Flag | Required | Description |
|------|----------|-------------|
| `--name` | Yes | Worktree name to merge |

**Merge behavior by PR state:**

| PR state | What happens |
|----------|-------------|
| PR merged | Full cleanup — worktree and branch removed, status → `done` |
| PR open | Worktree removed, branch preserved for PR, status → `merged-via-pr` |
| No PR, clean merge | Diff applied as unstaged changes, worktree + branch removed, status → `merged` |
| No PR, conflict | Patch saved to `.strawpot/patches/<name>.patch`, status → `conflict` |
| No PR, no changes | Worktree + branch removed, status → `merged` |

**Output (merged):**
```json
{
  "status": "merged",
  "name": "my-feature",
  "message": "Changes applied as unstaged modifications"
}
```

**Output (conflict):**
```json
{
  "status": "conflict",
  "name": "my-feature",
  "message": "Merge conflict detected — patch saved for manual resolution",
  "patch_path": ".strawpot/patches/my-feature.patch",
  "conflict_details": "error: patch failed: src/main.py:10"
}
```

### `discard` — Discard worktree without merging

Removes the worktree and branch without applying any changes. Use when
work is abandoned or superseded.

```bash
# Discard and delete remote branch
python scripts/worktree.py discard --name my-feature

# Discard but keep remote branch
python scripts/worktree.py discard --name my-feature --keep-remote
```

**Parameters:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--name` | Yes | — | Worktree name to discard |
| `--keep-remote` | No | `false` | Preserve remote branch |

**Output:**
```json
{
  "status": "discarded",
  "name": "my-feature",
  "message": "Worktree and branch removed",
  "remote_deleted": true
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
      "created_at": "2026-03-27T12:00:00+00:00",
      "status": "active"
    }
  ]
}
```

**Status values:**

| Status | Meaning |
|--------|---------|
| `active` | Worktree exists and is in use |
| `merged` | Changes merged locally, worktree cleaned up |
| `merged-via-pr` | PR-based merge, branch kept for open PR |
| `done` | PR merged, full cleanup complete |
| `conflict` | Merge attempted, patch saved to `.strawpot/patches/` |
| `discarded` | Explicitly abandoned |
| `stale` | In manifest but not in `git worktree list` output |

## Worktree layout

```
project/
├── .strawpot/
│   ├── worktrees.json          # Manifest tracking all worktrees
│   ├── worktrees/
│   │   ├── my-feature/         # Worktree directory
│   │   └── fix-auth/           # Another worktree
│   └── patches/
│       └── my-feature.patch    # Saved on merge conflict
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
