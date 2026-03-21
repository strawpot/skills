---
name: code-review
description: "Automated code review for pull requests using multiple specialized agents with confidence-based scoring. Use this skill whenever a task involves reviewing a pull request, auditing PR changes for bugs, checking CLAUDE.md compliance, or analyzing code changes in the context of git history. Triggers include: any mention of 'code review', 'review this PR', 'review pull request', 'check this PR', or requests to audit changes for bugs or compliance — even if the user just says 'review' in the context of a PR."
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

# Code Review

Automated code review for pull requests using multiple specialized agents with confidence-based scoring.

## Workflow

Given a pull request, follow these steps precisely:

### Step 1: Eligibility check

Use a subagent to check if the pull request (a) is closed, (b) is a draft, (c) does not need a code review (e.g. automated PR or trivially obvious), or (d) already has a code review from you. If so, do not proceed.

### Step 2: Gather CLAUDE.md files

Use a subagent to list file paths to any relevant CLAUDE.md files from the codebase: the root CLAUDE.md (if it exists) and any CLAUDE.md files in directories whose files the PR modified.

### Step 3: Summarize the change

Use a subagent to view the pull request and return a summary of the change.

### Step 4: Parallel code review

Launch 5 parallel subagents to independently review the change. Each agent returns a list of issues with the reason each was flagged (e.g. CLAUDE.md adherence, bug, historical git context):

1. **CLAUDE.md compliance** — Audit changes against the CLAUDE.md. Note that CLAUDE.md is guidance for Claude as it writes code, so not all instructions will be applicable during code review.
2. **Shallow bug scan** — Read file changes and scan for obvious bugs. Avoid reading extra context beyond the changes. Focus on large bugs, avoid nitpicks. Ignore likely false positives.
3. **Git history analysis** — Read git blame and history of modified code to identify bugs in light of historical context.
4. **Previous PR review** — Read previous pull requests that touched these files, and check for comments that may also apply to the current PR.
5. **Code comment compliance** — Read code comments in modified files and verify changes comply with any guidance in the comments.

### Step 5: Confidence scoring

For each issue found in Step 4, launch a parallel subagent that takes the PR, issue description, and list of CLAUDE.md files (from Step 2), and scores confidence on a scale of 0-100:

- **0**: False positive that doesn't stand up to light scrutiny, or a pre-existing issue.
- **25**: Might be a real issue, but may also be a false positive. Agent wasn't able to verify. If stylistic, not explicitly called out in relevant CLAUDE.md.
- **50**: Verified as real, but might be a nitpick or not happen often in practice. Not very important relative to the rest of the PR.
- **75**: Double-checked and very likely real, will be hit in practice. Existing approach in the PR is insufficient. Directly impacts functionality or is directly mentioned in relevant CLAUDE.md.
- **100**: Confirmed real, will happen frequently in practice. Evidence directly confirms this.

For issues flagged due to CLAUDE.md instructions, double check that the CLAUDE.md actually calls out that issue specifically.

### Step 6: Filter

Filter out any issues with a score less than 80. If no issues meet this threshold, skip to Step 8 with "no issues found."

### Step 7: Re-check eligibility

Use a subagent to repeat the eligibility check from Step 1, to make sure the PR is still eligible for review.

### Step 8: Post review comment

Use `gh pr comment` to post the result on the pull request.

## Comment format

When writing the comment:
- Keep output brief
- Avoid emojis
- Link and cite relevant code, files, and URLs

If issues were found:

```
### Code review

Found N issues:

1. <brief description> (CLAUDE.md says "<...>")

<link to file and line with full sha1 + line range>

2. <brief description> (bug due to <file and code snippet>)

<link to file and line with full sha1 + line range>
```

If no issues:

```
### Code review

No issues found. Checked for bugs and CLAUDE.md compliance.
```

### Agent return signal

After posting the PR comment, if no issues met the confidence threshold, output the literal string `NO_FURTHER_IMPROVEMENTS` as the final line of your return output (stdout / task result). Do NOT include this string in the `gh pr comment` body — it is a machine-readable signal for evaluator-in-the-loop workflows, not a human-facing message. This aligns with the convention used by other evaluator roles (docs-evaluator, skill-evaluator, etc.).

When linking to code, use the full git SHA — commands like `$(git rev-parse HEAD)` will not work since the comment is rendered as Markdown. Format: `https://github.com/owner/repo/blob/<full-sha>/path/to/file#L<start>-L<end>`. Provide at least 1 line of context before and after the issue.

## False positive guidance

The following are false positives and should not be flagged:

- Pre-existing issues
- Something that looks like a bug but is not actually a bug
- Pedantic nitpicks that a senior engineer wouldn't call out
- Issues that a linter, typechecker, or compiler would catch (missing imports, type errors, broken tests, formatting). Assume CI runs these separately.
- General code quality issues (test coverage, general security, poor documentation), unless explicitly required in CLAUDE.md
- Issues called out in CLAUDE.md but explicitly silenced in code (e.g. lint ignore comments)
- Changes in functionality that are likely intentional or directly related to the broader change
- Real issues on lines the user did not modify in their PR

## Notes

- Do not check build signal or attempt to build or typecheck the app. These run separately via CI.
- Use `gh` to interact with GitHub (fetch PRs, create comments), not web fetch.
