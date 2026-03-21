---
name: pipeline-orchestrator
description: "GitHub-based automation pipeline that advances issues through a label-driven state machine across all strawpot repos. Use this skill when running the automated pipeline, processing issues in batch, or advancing issues through pipeline stages. Trigger when the user mentions: run the pipeline, process issues automatically, advance stalled or approved issues, automated batch triage, plan approved issues, execute planned work, check pipeline status, unblock pipeline issues, resume the pipeline, set up pipeline labels, or cron-driven issue processing. Do NOT use for one-off manual triage of a single issue (use github-issues instead) or for manual PR review (use github-prs instead)."
metadata:
  strawpot:
    dependencies:
      - github-issues
      - github-prs
      - git-workflow
      - denden
    tools:
      gh:
        description: GitHub CLI (authenticated with org access)
        install:
          macos: brew install gh
          linux: sudo apt install gh
          windows: winget install GitHub.cli
    env:
      STRAWPOT_ORG:
        description: "GitHub organization name (default: strawpot)"
        required: false
      GITHUB_TOKEN:
        description: "GitHub token with org access (or use `gh auth login`)"
        required: false
---

# Pipeline Orchestrator

A label-driven state machine that advances GitHub issues through triage, planning, and implementation across all repos in the strawpot org. Designed to run on a cron interval (e.g., every hour). Each invocation is idempotent — it reads current label states and advances issues to the next stage.

This skill is the orchestration glue. It does NOT do triage, planning, or implementation directly — it delegates that work to specialized roles (`github-triager`, `implementation-planner`, `implementation-executor`, `implementer`) via denden.

## Invocation

When invoked, accept an optional mode argument:

| Mode | What it runs |
|---|---|
| `triage` | Loop 1 only — find and triage new issues |
| `plan` | Loop 2 only — plan approved issues |
| `execute` | Loop 3 only — execute planned issues |
| `all` | All three loops sequentially (default) |

If no mode is specified, default to `all`.

## State Machine

Issues move through states via `pipeline/*` labels. Only one `pipeline/*` state label should be active at a time (except `pipeline/sub-issue` which coexists with state labels).

```
 ┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
 │  (no label)  │────▶│pipeline/triage│────▶│pipeline/     │────▶│pipeline/     │
 │  new issue   │ L1  │ awaiting     │user │approved      │ L2  │planning      │
 └─────────────┘     │ approval     │     │              │     │              │
                      └──────────────┘     └──────────────┘     └──────┬───────┘
                                                                       │ L2
                      ┌──────────────┐     ┌──────────────┐     ┌──────▼───────┐
                      │pipeline/done │◀────│pipeline/     │◀────│pipeline/     │
                      │ merged       │user │review        │ L3  │planned       │
                      └──────────────┘     │ PR ready     │     │              │
                                           └──────────────┘     └──────────────┘

                      ┌──────────────┐
                      │pipeline/     │  ◀── any loop on failure
                      │blocked       │
                      └──────────────┘
```

### Label Reference

| Label | Set by | Description |
|---|---|---|
| `pipeline/triage` | Loop 1 | Triaged, awaiting human approval |
| `pipeline/approved` | Human | Approved for planning |
| `pipeline/planning` | Loop 2 | Being decomposed into sub-issues |
| `pipeline/planned` | Loop 2 | Sub-issues created, ready for execution |
| `pipeline/implementing` | Loop 3 | Sub-issues being worked on |
| `pipeline/review` | Loop 3 | PR(s) created, awaiting human review |
| `pipeline/done` | Human | Merged and complete |
| `pipeline/blocked` | Any loop | Failed or needs human intervention |
| `pipeline/sub-issue` | Loop 2 | Implementation sub-issue (excluded from triage) |

## Setup: Create Pipeline Labels

Before first use, create the required labels across all repos by running the bundled setup script:

```bash
bash scripts/setup-labels.sh [org-name]
```

The script defaults to `$STRAWPOT_ORG` or `strawpot`. It creates all 9 `pipeline/*` labels with color coding on every non-archived repo in the org. Safe to run multiple times — it uses `--force` to update existing labels.

## Discovering Repos

All loops start by discovering repos in the org:

```bash
ORG="${STRAWPOT_ORG:-strawpot}"
repos=$(gh repo list "$ORG" --no-archived --limit 100 --json nameWithOwner -q '.[].nameWithOwner')
```

## Code Patterns

The bash snippets below are **pseudocode templates** — adapt variable names, error handling, and control flow to your implementation. Variables like `$repo`, `$issue_number`, and `$sub_issues` represent values you extract from `gh` output during processing.

---

## Loop 1: Triage

**Purpose:** Find new issues across all repos, delegate triage to `github-triager`, and label for human review.

### Steps

1. **Find new issues** — issues with NO `pipeline/*` label and that are NOT pull requests:

```bash
for repo in $repos; do
  gh issue list --repo "$repo" --state open --json number,title,labels,isPullRequest \
    --jq '[.[] | select(.isPullRequest == false) | select(all(.labels[]; .name | startswith("pipeline/") | not))] | .[] | "\(.number) \(.title)"'
done
```

Issues with `pipeline/sub-issue` are automatically excluded since that label starts with `pipeline/`.

2. **For each new issue, delegate triage** to the `github-triager` role:

```bash
denden send "{\"delegate\":{\"delegateTo\":\"github-triager\",\"task\":{\"text\":\"Triage this GitHub issue: $repo#$issue_number. Read the issue, categorize it (bug/feature/enhancement/chore/docs), assign a priority label (p0-critical through p3-low), and post a triage summary comment explaining your rationale. Do NOT add pipeline labels — only add type and priority labels.\",\"returnFormat\":\"TEXT\"}}}"
```

3. **Add `pipeline/triage` label** after successful triage:

```bash
gh issue edit "$issue_number" --repo "$repo" --add-label "pipeline/triage"
```

4. **Post audit comment** on the issue:

```bash
gh issue comment "$issue_number" --repo "$repo" --body "🔄 **Pipeline:** Triaged by automation. Awaiting human approval.
- Add \`pipeline/approved\` label to advance to planning.
- Add \`pipeline/blocked\` to hold."
```

5. **On failure** — if triage delegation fails, add `pipeline/blocked` and comment with the error:

```bash
gh issue edit "$issue_number" --repo "$repo" --add-label "pipeline/blocked"
gh issue comment "$issue_number" --repo "$repo" --body "⚠️ **Pipeline:** Triage failed. Error: $error_message"
```

### Idempotency

An issue is only processed if it has zero `pipeline/*` labels. Once `pipeline/triage` is added, it won't be picked up again.

---

## Loop 2: Planning

**Purpose:** Break down approved issues into implementable sub-issues via `implementation-planner`.

### Steps

1. **Find approved issues:**

```bash
for repo in $repos; do
  gh issue list --repo "$repo" --state open --label "pipeline/approved" --json number,title \
    --jq '.[] | "\(.number) \(.title)"'
done
```

2. **Transition label** — move from `pipeline/approved` to `pipeline/planning`:

```bash
gh issue edit "$issue_number" --repo "$repo" --remove-label "pipeline/approved" --add-label "pipeline/planning"
gh issue comment "$issue_number" --repo "$repo" --body "🔄 **Pipeline:** Planning started. Decomposing into sub-issues..."
```

3. **Delegate to `implementation-planner`:**

```bash
denden send "{\"delegate\":{\"delegateTo\":\"implementation-planner\",\"task\":{\"text\":\"Break down this GitHub issue into ordered, implementable sub-issues: $repo#$issue_number. Read the issue thoroughly, analyze the codebase, and create sub-issues with clear acceptance criteria. Each sub-issue must include the label 'pipeline/sub-issue'. Post a planning summary comment on the parent issue with execution order and key decisions.\",\"returnFormat\":\"TEXT\"}}}"
```

4. **After successful planning** — verify sub-issue labels and transition parent:

```bash
# Verify pipeline/sub-issue label on each sub-issue created by the planner
for sub_issue in $sub_issues; do
  gh issue edit "$sub_issue" --repo "$repo" --add-label "pipeline/sub-issue"
done

# Transition parent
gh issue edit "$issue_number" --repo "$repo" --remove-label "pipeline/planning" --add-label "pipeline/planned"
gh issue comment "$issue_number" --repo "$repo" --body "✅ **Pipeline:** Planning complete. Sub-issues created. Ready for execution."
```

5. **On failure:**

```bash
gh issue edit "$issue_number" --repo "$repo" --remove-label "pipeline/planning" --add-label "pipeline/blocked"
gh issue comment "$issue_number" --repo "$repo" --body "⚠️ **Pipeline:** Planning failed. Error: $error_message
Manually review and either retry (remove \`pipeline/blocked\`, add \`pipeline/approved\`) or close."
```

### Idempotency

- Only `pipeline/approved` triggers planning — issues already in `pipeline/planning` or `pipeline/planned` are skipped.
- If planning was interrupted (issue stuck in `pipeline/planning`), manually move it back to `pipeline/approved` to retry.

---

## Loop 3: Execution

**Purpose:** Implement planned sub-issues and create PRs via `implementation-executor` or `implementer`.

### Steps

1. **Find parent issues ready for execution.** Check both `pipeline/planned` (new) and `pipeline/implementing` (resuming interrupted runs):

```bash
for repo in $repos; do
  # New parents ready for execution
  gh issue list --repo "$repo" --state open --label "pipeline/planned" --json number,title \
    --jq '.[] | "\(.number) \(.title)"'

  # Parents with in-progress execution (resume)
  gh issue list --repo "$repo" --state open --label "pipeline/implementing" --json number,title \
    --jq '.[] | "\(.number) \(.title)"'
done
```

2. **For new parents (`pipeline/planned`), transition label:**

```bash
gh issue edit "$issue_number" --repo "$repo" --remove-label "pipeline/planned" --add-label "pipeline/implementing"
gh issue comment "$issue_number" --repo "$repo" --body "🔄 **Pipeline:** Execution started. Working through sub-issues..."
```

For parents already in `pipeline/implementing`, skip the transition — just resume from where it left off.

3. **Find sub-issues** for the parent. Sub-issues reference the parent in their body (look for `#N` references):

```bash
gh issue list --repo "$repo" --state open --label "pipeline/sub-issue" --json number,title,body,labels \
  --jq "[.[] | select(.body | contains(\"#$issue_number\"))] | sort_by(.number) | .[]"
```

4. **Skip completed sub-issues** — any sub-issue already labeled `pipeline/review` has a PR and should be skipped. Process only sub-issues without `pipeline/review`.

5. **For each remaining sub-issue, delegate execution.** Use `implementation-executor` for structured plans (created by `implementation-planner`). Fall back to `implementer` if the executor reports no structured plan:

```bash
# Try implementation-executor first
result=$(denden send "{\"delegate\":{\"delegateTo\":\"implementation-executor\",\"task\":{\"text\":\"Execute this sub-issue: $repo#$sub_issue_number. It is part of parent issue $repo#$issue_number. Read the sub-issue, implement the changes following the acceptance criteria, run tests, and open a PR. Reference the sub-issue in the PR description.\",\"returnFormat\":\"TEXT\"}}}")

# If executor fails, fall back to implementer
if [ $? -ne 0 ]; then
  result=$(denden send "{\"delegate\":{\"delegateTo\":\"implementer\",\"task\":{\"text\":\"Implement this GitHub issue: $repo#$sub_issue_number. Read the issue, implement the required changes, run tests, and open a PR. Reference issue #$sub_issue_number and parent issue #$issue_number in the PR.\",\"returnFormat\":\"TEXT\"}}}")
fi
```

6. **After each sub-issue completes**, add review label:

```bash
gh issue edit "$sub_issue_number" --repo "$repo" --add-label "pipeline/review"
```

7. **Check if all sub-issues are done.** When all sub-issues for a parent have `pipeline/review`:

```bash
remaining=$(gh issue list --repo "$repo" --state open --label "pipeline/sub-issue" --json number,body,labels \
  --jq "[.[] | select(.body | contains(\"#$issue_number\")) | select(any(.labels[]; .name == \"pipeline/review\") | not)] | length")

if [ "$remaining" -eq 0 ]; then
  gh issue edit "$issue_number" --repo "$repo" --remove-label "pipeline/implementing" --add-label "pipeline/review"
  gh issue comment "$issue_number" --repo "$repo" --body "✅ **Pipeline:** All sub-issues implemented. PRs ready for human review.
Review and merge PRs, then add \`pipeline/done\` to close."
fi
```

8. **On failure:**

```bash
gh issue edit "$issue_number" --repo "$repo" --remove-label "pipeline/implementing" --add-label "pipeline/blocked"
gh issue comment "$issue_number" --repo "$repo" --body "⚠️ **Pipeline:** Execution failed on sub-issue #$sub_issue_number. Error: $error_message
Manually review, fix the blocker, then remove \`pipeline/blocked\` and add \`pipeline/planned\` to retry."
```

### Idempotency & Resumability

- Sub-issues already labeled `pipeline/review` are skipped (already have PRs).
- Parents in `pipeline/implementing` are resumed, not restarted — only unfinished sub-issues are processed.
- This makes the pipeline fully resumable after interruption.

---

## Output

After each run, produce a summary report listing what was processed:

```
## Pipeline Run Summary

**Mode:** all | triage | plan | execute
**Org:** strawpot
**Time:** 2026-03-20T14:00:00Z

### Triage (Loop 1)
- Processed: 3 new issues
  - strawpot/denden#42 — "Add retry logic to gRPC calls" → pipeline/triage
  - strawpot/skills#18 — "Skill X not triggering" → pipeline/triage
  - strawpot/strawhub#7 — "Search broken on mobile" → pipeline/triage
- Errors: 0

### Planning (Loop 2)
- Processed: 1 approved issue
  - strawpot/denden#38 — "Implement batch delegation" → pipeline/planned (4 sub-issues)
- Errors: 0

### Execution (Loop 3)
- Processed: 2 sub-issues
  - strawpot/denden#39 — PR #45 created → pipeline/review
  - strawpot/denden#40 — PR #46 created → pipeline/review
- Parents completed: 0 (2 sub-issues remaining)
- Errors: 0

### Blocked
- No new blocked issues
```

If nothing was processed in a loop, report "No issues in this state" rather than omitting the section.

---

## Error Handling

Every state transition follows this pattern:

1. **Before work:** Transition to the "in-progress" label (e.g., `planning`, `implementing`)
2. **On success:** Transition to the "complete" label (e.g., `planned`, `review`)
3. **On failure:** Transition to `pipeline/blocked` with an error comment

The `pipeline/blocked` label is an escape hatch. To unblock:
- Fix the underlying issue
- Remove `pipeline/blocked`
- Add the appropriate label to re-enter the pipeline (e.g., `pipeline/approved` to retry planning)

## Audit Trail

Every label change MUST be accompanied by a GitHub comment explaining what happened and what the next step is. This makes the pipeline fully auditable — anyone reading the issue can understand its journey through the pipeline.

Comment format:
```
🔄 **Pipeline:** <action description>
<next steps or instructions>
```

## Rate Limiting

When processing many issues across many repos:
- Process repos sequentially to avoid GitHub API rate limits
- Add a small delay between delegations to avoid overwhelming the orchestrator
- If rate-limited, log the error and continue with the next issue — it will be picked up on the next cron run

## Running on a Schedule

Set up a cron job to run the pipeline at regular intervals:

```bash
# Run all loops every hour
strawpot cron create --schedule "0 * * * *" --command "pipeline-orchestrator all"

# Or run loops at different intervals for finer control
strawpot cron create --schedule "*/30 * * * *" --command "pipeline-orchestrator triage"
strawpot cron create --schedule "0 * * * *" --command "pipeline-orchestrator plan"
strawpot cron create --schedule "0 */2 * * *" --command "pipeline-orchestrator execute"
```

## Quick Reference

| Want to... | Do this |
|---|---|
| Approve an issue for planning | Add `pipeline/approved` label |
| Block an issue | Add `pipeline/blocked` label |
| Unblock and retry planning | Remove `pipeline/blocked`, add `pipeline/approved` |
| Unblock and retry execution | Remove `pipeline/blocked`, add `pipeline/planned` |
| Mark as complete after merge | Add `pipeline/done` label |
| Exclude an issue from pipeline | Don't add any `pipeline/*` label (it stays untriaged) |
| Check pipeline status | `gh issue list --label "pipeline/<state>"` per repo |
| Set up labels on new repo | `bash scripts/setup-labels.sh` |
