---
name: review-pr
description: "Comprehensive pull request review for bugs, code quality, and project guideline compliance. Use this skill whenever a task involves reviewing a PR, auditing code changes, or improving code quality before merge. Triggers include: 'review PR', 'review this pull request', 'check code quality', 'audit changes', 'review my changes', or any request to analyze code for bugs or compliance before merging."
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

# PR Review

Provide a comprehensive code review for a pull request.

## Workflow

### 1. Gather context

- Run `git diff --name-only` to identify changed files
- Check if PR exists: `gh pr view`
- Read the PR diff: `gh pr diff` or `git diff`
- Locate relevant CLAUDE.md files (root and in modified directories)

### 2. Review the changes

For each changed file, analyze:

- **Project guideline compliance**: Verify adherence to rules in CLAUDE.md — import patterns, framework conventions, style, error handling, testing practices, naming conventions
- **Bug detection**: Logic errors, null/undefined handling, race conditions, memory leaks, security vulnerabilities, performance problems
- **Error handling**: Silent failures, empty catch blocks, missing user feedback, overly broad exception catching
- **Test coverage**: Critical untested code paths, missing edge cases, brittle tests coupled to implementation details
- **Code comments**: Accuracy vs actual code, outdated references, misleading documentation

### 3. Score each issue

Rate confidence from 0-100:

- **0-25**: Likely false positive or pre-existing issue
- **26-50**: Minor nitpick not explicitly in CLAUDE.md
- **51-75**: Valid but low-impact
- **76-90**: Important, requires attention
- **91-100**: Critical bug or explicit CLAUDE.md violation

**Only report issues with confidence >= 80.**

### 4. Filter false positives

Do not flag:

- Pre-existing issues
- Pedantic nitpicks a senior engineer wouldn't call out
- Issues a linter, typechecker, or compiler would catch (assume CI runs these)
- General code quality issues unless explicitly required in CLAUDE.md
- Issues called out in CLAUDE.md but silenced in code (e.g. lint ignore comments)
- Changes in functionality that are likely intentional
- Real issues on lines the user did not modify

### 5. Report findings

```markdown
# PR Review Summary

## Critical Issues (X found)
- Issue description [file:line]

## Important Issues (X found)
- Issue description [file:line]

## Suggestions (X found)
- Suggestion [file:line]

## Strengths
- What's well-done in this PR
```

If no issues with confidence >= 80, report: "No issues found. Checked for bugs and CLAUDE.md compliance."

## Notes

- Do not attempt to build or typecheck the app — CI runs these separately
- Use `gh` to interact with GitHub, not web fetch
- Link and cite relevant code with file paths and line numbers
- Keep output brief and actionable
