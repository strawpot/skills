---
name: github-issues
description: "Knowledge for working with GitHub issues via the gh CLI. Use this skill when triaging, creating, updating, labeling, assigning, or closing issues on any GitHub repository. Covers issue lifecycle, triage workflows, priority labels, and search queries."
metadata:
  strawpot:
    tools:
      gh:
        description: GitHub CLI
        install:
          macos: brew install gh
          linux: sudo apt install gh
    env:
      GITHUB_TOKEN:
        description: GitHub personal access token (or use `gh auth login`)
        required: false
---

# GitHub Issues

Manage GitHub issues using the `gh` CLI. Always prefer `gh` over the
REST API — it handles auth, pagination, and formatting automatically.

## Authentication

```bash
# Interactive login (sets up token automatically)
gh auth login

# Or set token directly
export GITHUB_TOKEN="ghp_..."
```

## List Issues

```bash
# List open issues (default: 30)
gh issue list --repo owner/repo

# With filters
gh issue list --repo owner/repo --label "bug" --assignee "@me"
gh issue list --repo owner/repo --state closed --limit 10
gh issue list --repo owner/repo --milestone "v1.0"

# Search with queries
gh issue list --repo owner/repo --search "is:open label:bug sort:created-desc"
gh issue list --repo owner/repo --search "is:open no:assignee"
```

## View an Issue

```bash
# View issue details (renders markdown)
gh issue view 42 --repo owner/repo

# JSON output for parsing
gh issue view 42 --repo owner/repo --json title,body,labels,assignees,state,comments
```

## Create an Issue

```bash
# Interactive
gh issue create --repo owner/repo

# Non-interactive (preferred for automation)
gh issue create --repo owner/repo \
  --title "Bug: widget crashes on empty input" \
  --body "## Steps to reproduce
1. Open widget
2. Submit empty form

## Expected
Validation error

## Actual
Crash with stack trace" \
  --label "bug,priority:high" \
  --assignee "username"
```

## Update an Issue

```bash
# Edit title or body
gh issue edit 42 --repo owner/repo --title "Updated title"
gh issue edit 42 --repo owner/repo --body "Updated description"

# Add labels
gh issue edit 42 --repo owner/repo --add-label "priority:high,needs-triage"

# Remove labels
gh issue edit 42 --repo owner/repo --remove-label "needs-triage"

# Assign / unassign
gh issue edit 42 --repo owner/repo --add-assignee "username"
gh issue edit 42 --repo owner/repo --remove-assignee "username"

# Set milestone
gh issue edit 42 --repo owner/repo --milestone "v1.0"
```

## Close / Reopen

```bash
# Close with a reason
gh issue close 42 --repo owner/repo --reason completed
gh issue close 42 --repo owner/repo --reason "not planned" --comment "Closing — out of scope for v1"

# Reopen
gh issue reopen 42 --repo owner/repo
```

## Comment on an Issue

```bash
gh issue comment 42 --repo owner/repo --body "Investigated — root cause is X. Fix incoming."
```

## Pin / Unpin

```bash
gh issue pin 42 --repo owner/repo
gh issue unpin 42 --repo owner/repo
```

## Transfer

```bash
gh issue transfer 42 --repo owner/repo destination-owner/destination-repo
```

## Triage Workflow

When triaging issues for a project:

1. **Fetch untriaged issues:**
   ```bash
   gh issue list --repo owner/repo --search "is:open no:label sort:created-asc" --limit 50
   ```

2. **For each issue, read and classify:**
   ```bash
   gh issue view <number> --repo owner/repo --json title,body,comments
   ```

3. **Apply labels by type:**
   - `bug` — Broken behavior
   - `feature` — New capability request
   - `enhancement` — Improvement to existing feature
   - `question` — Needs clarification from reporter
   - `duplicate` — Already tracked (close with link)

4. **Apply priority labels:**
   - `priority:critical` — Data loss, security, or complete breakage
   - `priority:high` — Major feature broken, blocks users
   - `priority:medium` — Important but has workaround
   - `priority:low` — Nice to have, cosmetic, minor

5. **Assign or escalate:**
   ```bash
   # Assign to the right person
   gh issue edit <number> --repo owner/repo --add-assignee "username" --add-label "bug,priority:high"

   # Or leave for team discussion
   gh issue edit <number> --repo owner/repo --add-label "needs-discussion"
   ```

## Bulk Operations

```bash
# Close all issues with a label
gh issue list --repo owner/repo --label "wontfix" --json number --jq '.[].number' | \
  xargs -I{} gh issue close {} --repo owner/repo --reason "not planned"

# Add label to all open bugs
gh issue list --repo owner/repo --label "bug" --json number --jq '.[].number' | \
  xargs -I{} gh issue edit {} --repo owner/repo --add-label "needs-review"
```

## JSON Fields Reference

Available fields for `--json`:
`assignees`, `author`, `body`, `closed`, `closedAt`, `comments`,
`createdAt`, `id`, `labels`, `milestone`, `number`, `projectCards`,
`reactionGroups`, `state`, `title`, `updatedAt`, `url`.
