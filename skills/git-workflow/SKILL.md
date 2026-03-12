---
name: git-workflow
description: "Knowledge for Git branching, committing, pushing, rebasing, and merging workflows. Use this skill when implementing features, fixing bugs, or managing branches. Covers branch naming conventions, commit message format, conflict resolution, worktree usage, and safe push/pull patterns."
---

# Git Workflow

Practical Git workflows for feature development, bug fixes, and
release management.

## Branch Naming

```
<type>/<short-description>

# Examples
feature/add-user-auth
fix/widget-crash-on-empty-input
chore/update-dependencies
docs/api-reference
refactor/extract-parser-module
```

Types: `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`.

Keep branch names lowercase, use hyphens, and keep them short.

## Starting Work

```bash
# Always start from an up-to-date main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature

# Or use a worktree for parallel work
git worktree add ../my-feature feature/my-feature
```

## Commit Messages

Format:
```
<type>: <short summary>

<optional body — explain why, not what>

<optional footer — references, breaking changes>
```

Examples:
```
fix: prevent crash on empty widget input

The form submission handler assumed input was always non-null.
Added validation before processing.

Closes #42
```

```
feature: add rate limiting to API endpoints

Adds token-bucket rate limiter with configurable limits per
endpoint. Defaults to 100 req/min for standard endpoints.
```

Types: `feature`, `fix`, `chore`, `docs`, `refactor`, `test`, `ci`.

Guidelines:
- First line ≤ 72 characters
- Use imperative mood ("add", not "added" or "adds")
- Body wraps at 72 characters
- Reference issues in footer with `Closes #N` or `Refs #N`

## Staging and Committing

```bash
# Stage specific files (preferred — avoids accidental commits)
git add src/parser.py tests/test_parser.py

# Review what you're about to commit
git diff --staged

# Commit
git commit -m "fix: handle null input in parser"

# Stage and commit tracked files (skip untracked)
git commit -am "chore: update error messages"
```

**Never commit:**
- `.env` files or secrets
- Large binaries or build artifacts
- IDE-specific files (`.idea/`, `.vscode/` unless shared config)

## Pushing

```bash
# First push — set upstream
git push -u origin feature/my-feature

# Subsequent pushes
git push

# After rebasing (force push safely)
git push --force-with-lease
```

**Rules:**
- Never `git push --force` to `main` or `master`
- Always use `--force-with-lease` instead of `--force` (prevents overwriting others' work)
- Push regularly to back up your work

## Keeping Up to Date

```bash
# Rebase onto latest main (preferred — clean linear history)
git fetch origin
git rebase origin/main

# Or merge (if rebase is too complex)
git merge origin/main
```

Prefer **rebase** for feature branches. Use **merge** only when the
branch has been shared or has complex history.

## Resolving Conflicts

```bash
# During rebase — conflicts appear one commit at a time
git status                    # See conflicted files
# ... edit files to resolve conflicts ...
git add <resolved-files>
git rebase --continue

# Abort if it gets messy
git rebase --abort

# During merge
git status                    # See conflicted files
# ... edit files to resolve conflicts ...
git add <resolved-files>
git commit                    # Merge commit is created
```

Conflict markers:
```
<<<<<<< HEAD
your changes
=======
their changes
>>>>>>> feature/other
```

## Worktrees

Worktrees let you work on multiple branches simultaneously without
stashing or switching.

```bash
# Create a worktree for a new branch
git worktree add ../feature-x feature/feature-x

# Create a worktree for an existing branch
git worktree add ../hotfix fix/urgent-bug

# List worktrees
git worktree list

# Remove when done
git worktree remove ../feature-x
```

Use worktrees when:
- You need to review a PR while working on something else
- You're running tests on one branch while coding on another
- You need to compare behavior across branches

## Stashing

```bash
# Save current work
git stash

# Save with a name
git stash push -m "WIP: parser refactor"

# List stashes
git stash list

# Restore latest stash
git stash pop

# Restore a specific stash
git stash pop stash@{2}

# Drop a stash
git stash drop stash@{0}
```

## Undoing Things

```bash
# Undo last commit (keep changes staged)
git reset --soft HEAD~1

# Undo last commit (keep changes unstaged)
git reset HEAD~1

# Discard changes in a specific file
git checkout -- path/to/file

# Revert a commit (creates a new undo commit — safe for shared branches)
git revert <commit-hash>
```

**Warning:** `git reset --hard` destroys uncommitted work. Use
`git stash` first if unsure.

## Tags and Releases

```bash
# Create an annotated tag
git tag -a v1.2.0 -m "Release v1.2.0"

# Push tags
git push origin v1.2.0
git push origin --tags

# List tags
git tag --list "v1.*"
```

## Useful Shortcuts

```bash
# View concise log
git log --oneline -20

# See what changed in a range
git diff main...HEAD
git log main..HEAD --oneline

# Find which commit introduced a bug
git bisect start
git bisect bad HEAD
git bisect good v1.0.0
# ... test each commit git bisect suggests ...
git bisect reset

# Check who last modified a line
git blame path/to/file

# Clean up merged branches
git branch --merged main | grep -v main | xargs git branch -d
```
