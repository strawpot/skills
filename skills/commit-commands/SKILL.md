---
name: commit-commands
description: "Streamline git workflow with commands for committing, pushing, creating pull requests, and cleaning up stale branches. Use this skill whenever a task involves committing changes, pushing and opening a PR in one step, or cleaning up local branches that have been deleted on the remote. Triggers include: 'commit', 'commit and push', 'open a PR', 'create PR', 'clean up branches', 'remove gone branches', or any request to streamline git operations."
metadata:
  strawpot:
    tools:
      gh:
        description: GitHub CLI
        install:
          macos: brew install gh
          linux: apt install gh
          windows: winget install GitHub.cli
---

# Commit Commands

Streamline git workflow with simple commands for committing, pushing, and creating pull requests.

## Commit

Create a single git commit from current changes.

1. Review the current state:
   - `git status`
   - `git diff HEAD` (staged and unstaged changes)
   - `git branch --show-current`
   - `git log --oneline -10` (recent commits for message style)
2. Stage relevant files with `git add`
3. Create a single commit with an appropriate message based on the changes

Keep the commit message concise and descriptive. Follow the repository's existing commit message conventions visible in recent history.

## Commit, Push, and PR

Commit, push, and open a pull request in one step.

1. Review the current state:
   - `git status`
   - `git diff HEAD`
   - `git branch --show-current`
2. Create a new branch if currently on main/master
3. Create a single commit with an appropriate message
4. Push the branch to origin
5. Create a pull request using `gh pr create`

Execute all steps in a single pass. Do not pause between steps.

## Clean Gone Branches

Clean up all local git branches marked as `[gone]` — branches deleted on the remote but still existing locally — including removing associated worktrees.

1. List branches to identify any with `[gone]` status:
   ```bash
   git branch -v
   ```
   Branches with a `+` prefix have associated worktrees that must be removed before deletion.

2. Identify worktrees that need removal:
   ```bash
   git worktree list
   ```

3. Remove worktrees and delete `[gone]` branches:
   ```bash
   git branch -v | grep '\[gone\]' | sed 's/^[+* ]//' | awk '{print $1}' | while read branch; do
     echo "Processing branch: $branch"
     worktree=$(git worktree list | grep "\\[$branch\\]" | awk '{print $1}')
     if [ ! -z "$worktree" ] && [ "$worktree" != "$(git rev-parse --show-toplevel)" ]; then
       echo "  Removing worktree: $worktree"
       git worktree remove --force "$worktree"
     fi
     echo "  Deleting branch: $branch"
     git branch -D "$branch"
   done
   ```

If no branches are marked as `[gone]`, report that no cleanup was needed.
