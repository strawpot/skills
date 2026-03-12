---
name: github-prs
description: "Knowledge for working with GitHub pull requests via the gh CLI. Use this skill when creating, reviewing, approving, requesting changes, commenting on, or merging pull requests. Covers PR lifecycle, review checklists, merge strategies, and CI status checks."
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

# GitHub Pull Requests

Manage GitHub pull requests using the `gh` CLI.

## List PRs

```bash
# Open PRs (default)
gh pr list --repo owner/repo

# With filters
gh pr list --repo owner/repo --state merged --limit 10
gh pr list --repo owner/repo --author "username"
gh pr list --repo owner/repo --label "needs-review"
gh pr list --repo owner/repo --search "is:open review:required sort:created-asc"

# PRs needing my review
gh pr list --repo owner/repo --search "is:open review-requested:@me"
```

## View a PR

```bash
# Rendered view
gh pr view 123 --repo owner/repo

# JSON for parsing
gh pr view 123 --repo owner/repo --json title,body,state,mergeable,reviewDecision,statusCheckRollup,files

# View the diff
gh pr diff 123 --repo owner/repo
```

## Create a PR

```bash
# From current branch (interactive)
gh pr create --repo owner/repo

# Non-interactive (preferred for automation)
gh pr create --repo owner/repo \
  --title "Add input validation to widget" \
  --body "## Summary
- Adds client-side validation for empty inputs
- Adds server-side validation as fallback
- Closes #42

## Test plan
- [x] Unit tests for validator
- [x] Integration test for form submission
- [ ] Manual test on staging" \
  --base main \
  --label "enhancement"

# Draft PR
gh pr create --repo owner/repo --title "WIP: new feature" --draft

# With reviewers
gh pr create --repo owner/repo \
  --title "Fix auth bug" \
  --reviewer "username1,username2"
```

## Edit a PR

```bash
# Update title or body
gh pr edit 123 --repo owner/repo --title "Updated title"
gh pr edit 123 --repo owner/repo --body "Updated description"

# Add/remove labels
gh pr edit 123 --repo owner/repo --add-label "ready-for-review"
gh pr edit 123 --repo owner/repo --remove-label "wip"

# Add reviewers
gh pr edit 123 --repo owner/repo --add-reviewer "username"

# Convert draft to ready
gh pr ready 123 --repo owner/repo
```

## Review a PR

```bash
# Approve
gh pr review 123 --repo owner/repo --approve --body "LGTM — clean implementation."

# Request changes
gh pr review 123 --repo owner/repo --request-changes --body "See inline comments. Main concerns:
1. Missing error handling in parser
2. No test for edge case X"

# Comment (neither approve nor reject)
gh pr review 123 --repo owner/repo --comment --body "A few questions before I can approve."
```

## Comment on a PR

```bash
# General comment
gh pr comment 123 --repo owner/repo --body "Tested locally, works as expected."
```

## Check CI Status

```bash
# View all checks
gh pr checks 123 --repo owner/repo

# Wait for checks to pass (blocks until done)
gh pr checks 123 --repo owner/repo --watch
```

## Merge a PR

```bash
# Merge commit (default)
gh pr merge 123 --repo owner/repo

# Squash merge (preferred for clean history)
gh pr merge 123 --repo owner/repo --squash

# Rebase merge
gh pr merge 123 --repo owner/repo --rebase

# Auto-merge when checks pass
gh pr merge 123 --repo owner/repo --auto --squash

# Delete branch after merge
gh pr merge 123 --repo owner/repo --squash --delete-branch

# Merge without confirmation prompt
gh pr merge 123 --repo owner/repo --squash --delete-branch --yes
```

## Close Without Merging

```bash
gh pr close 123 --repo owner/repo --comment "Superseded by #456"
gh pr close 123 --repo owner/repo --delete-branch
```

## Checkout a PR Locally

```bash
gh pr checkout 123 --repo owner/repo
```

## Review Checklist

When reviewing a PR, check:

1. **Purpose** — Does the PR description explain *why* this change exists?
2. **Scope** — Is this one logical change, or should it be split?
3. **Tests** — Are there tests? Do they cover edge cases?
4. **Breaking changes** — Does this break the public API or config format?
5. **Security** — No secrets in code? Input validation? Auth checks?
6. **Performance** — Any N+1 queries, unbounded loops, or memory leaks?
7. **Documentation** — Are public APIs, config options, and CLI flags documented?
8. **CI** — Are all checks passing?

## Merge Strategy Guide

| Strategy | When to use |
|----------|------------|
| **Squash** | Most PRs. Clean history, one commit per feature/fix. |
| **Merge commit** | Large PRs with meaningful individual commits worth preserving. |
| **Rebase** | Linear history preferred, small PRs with clean commits. |

Default recommendation: **squash merge** with branch deletion.

## JSON Fields Reference

Available fields for `--json`:
`additions`, `assignees`, `author`, `baseRefName`, `body`, `changedFiles`,
`closed`, `closedAt`, `comments`, `commits`, `createdAt`, `deletions`,
`files`, `headRefName`, `headRefOid`, `id`, `isCrossRepository`, `isDraft`,
`labels`, `latestReviews`, `maintainerCanModify`, `mergeable`,
`mergeCommit`, `mergedAt`, `mergedBy`, `milestone`, `number`,
`potentialMergeCommit`, `projectCards`, `reactionGroups`, `reviewDecision`,
`reviewRequests`, `reviews`, `state`, `statusCheckRollup`, `title`,
`updatedAt`, `url`.
