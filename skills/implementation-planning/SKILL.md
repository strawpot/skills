---
name: implementation-planning
description: "Methodology for breaking down GitHub issues into ordered, implementable sub-issues. Use this skill when planning implementation work — decomposing a feature or bug fix into small, dependency-ordered tasks with clear acceptance criteria and implementation hints. Trigger whenever the user asks to plan work, break down an issue, decompose a feature into tasks, create sub-issues, apply complexity sizing labels (S/M/L/XL), or order tasks by dependency. Also use when the user says things like 'how should we implement this', 'break this into steps', 'create a plan for this issue', or 'what's the implementation order'. Covers analysis frameworks, sub-issue templates, complexity estimation, and dependency ordering."
metadata:
  strawpot:
    dependencies:
      - github-issues
    env:
      GITHUB_TOKEN:
        description: GitHub personal access token (or use `gh auth login`)
        required: false
    tools:
      gh:
        description: GitHub CLI
        install:
          macos: brew install gh
          linux: sudo apt install gh
          windows: winget install GitHub.cli
---

# Implementation Planning

A structured methodology for breaking down GitHub issues into small,
ordered, implementable sub-issues. The goal is to produce a work queue
that an implementer can pick up one issue at a time and execute
without needing to understand the full picture.

## Core Principle

**Break it down until each piece is boring.** If a sub-issue feels
complex, it's not broken down enough. Each sub-issue should take a
single focused session to implement — one branch, one PR, one review.

## Analysis Framework

Before decomposing, understand the issue deeply. Follow this sequence:

### 1. Clarify the goal

Read the parent issue and answer:

- **What** is the desired end state? (behavior, output, user experience)
- **Why** does this matter? (business context, user impact)
- **What does "done" look like?** (observable, testable outcome)
- **What is explicitly out of scope?** (prevent scope creep)

If any of these are unclear from the issue, add a comment asking for
clarification before proceeding. Don't guess at intent.

### 2. Map the codebase

Explore the relevant parts of the codebase to understand:

- **Where** does this change live? (files, modules, packages)
- **What exists already?** (patterns to follow, code to reuse)
- **What are the boundaries?** (interfaces, API contracts, module edges)
- **What could break?** (dependencies, consumers, side effects)

Use the project's `CLAUDE.md` or `CONTRIBUTING.md` for conventions.

### 3. Identify the work units

Decompose the change into discrete, independently-implementable units.
Each unit should:

- Touch a small, well-defined area of the codebase
- Have a clear input (precondition) and output (deliverable)
- Be testable on its own
- Be reviewable in isolation (a reviewer shouldn't need to see other
  sub-issues to understand this one)

Common decomposition strategies:

- **By layer**: data model → business logic → API → UI
- **By feature slice**: each slice is end-to-end but narrow
- **By dependency**: foundational pieces first, dependent pieces after
- **By risk**: risky/uncertain pieces first (fail fast)

Prefer **vertical slices** when possible — they deliver incremental
value and surface integration issues early. Use **horizontal layers**
only when the work is genuinely sequential (e.g., need the database
schema before the API).

### 4. Order by dependency

Arrange sub-issues so each one can be implemented assuming all
previous ones are merged. Rules:

1. **No forward references.** Sub-issue N must not depend on code from
   sub-issue N+1.
2. **Shared foundations first.** Types, interfaces, schemas, configs go
   early.
3. **Risky items early.** If a sub-issue might invalidate the approach,
   put it first.
4. **Tests alongside implementation.** Don't batch tests at the end —
   each sub-issue includes its own tests.

### 5. Estimate complexity

Apply a complexity label to each sub-issue:

- **`size/S`** — Small. Obvious change, few files, well-understood
  pattern. ~30 min implementation.
- **`size/M`** — Medium. Moderate scope, some decisions to make, but
  approach is clear. ~1-2 hours implementation.
- **`size/L`** — Large. Significant scope, multiple files, may require
  design decisions. ~half-day implementation. **Consider splitting
  further.**
- **`size/XL`** — Too large. **Must be split.** An XL sub-issue means
  the decomposition isn't done yet. Never create a sub-issue labeled
  XL — split it into smaller pieces first.

If total estimated complexity seems disproportionate to the parent
issue, revisit — you may be over-engineering or missing a simpler
approach.

## Sub-Issue Template

Each sub-issue should follow this structure:

```markdown
## Context

[1-2 sentences linking to the parent issue and explaining where this
sub-issue fits in the overall plan.]

Parent: #<parent-issue-number>
Order: <N> of <total> (implement after #<previous-sub-issue>)

## Task

[Clear, specific description of what to implement. Be prescriptive —
tell the implementer exactly what to build, not just what to achieve.]

## Implementation Hints

- **Files to modify**: `path/to/file.ts`, `path/to/other.ts`
- **Patterns to follow**: [reference existing similar code]
- **Key decisions**: [any design choices already made]
- **Watch out for**: [gotchas, edge cases, tricky parts]

## Acceptance Criteria

- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Tests added/updated for the change]
- [ ] [No regressions in existing tests]
```

### Creating sub-issues with `gh`

Use the `gh` CLI to create each sub-issue. Pass the template content as
the issue body:

```bash
gh issue create --repo owner/repo \
  --title "1/4: Add PlanResult type to planning/types.ts" \
  --body "## Context

Part of the implementation plan for #42.
Order: 1 of 4

## Task

Define the \`PlanResult\` type that the planning module returns...

## Implementation Hints

- **Files to modify**: \`src/planning/types.ts\`
- **Patterns to follow**: see \`TaskResult\` in the same file
- **Watch out for**: export from the barrel file \`index.ts\`

## Acceptance Criteria

- [ ] \`PlanResult\` type is exported from \`planning/types.ts\`
- [ ] Existing types are unchanged
- [ ] Type-checks pass (\`tsc --noEmit\`)" \
  --label "sub-issue,size/S,status/planned"
```

After creating all sub-issues, post the planning summary on the parent:

```bash
gh issue comment 42 --repo owner/repo --body "## Implementation Plan
..."
```

And transition the parent label:

```bash
gh issue edit 42 --repo owner/repo \
  --remove-label "status/approved" --add-label "status/planned"
```

## Planning Output

After completing the analysis, post a **planning summary** as a comment
on the parent issue:

```markdown
## Implementation Plan

**Scope**: [1 sentence summary of what this plan covers]
**Sub-issues**: <N> tasks, estimated [S/M/L] total effort
**Approach**: [1-2 sentences on the decomposition strategy chosen]

### Execution Order

1. #<number> — <title> (`size/S`)
2. #<number> — <title> (`size/M`)
3. #<number> — <title> (`size/S`)
...

### Dependencies & Risks

- [Any external dependencies or blockers]
- [Risky assumptions that might change the plan]
- [Areas where the implementer should ask for help]

### Out of Scope

- [Things explicitly deferred to future work]
```

## Pipeline Integration

This skill is designed to work within a label-based pipeline:

| When | Do | Label transition |
|------|----|-----------------|
| Issue arrives with `status/approved` | Start planning | → `status/planning` |
| Sub-issues created, plan posted | Mark parent done | → `status/planned` |
| Sub-issue picked up by implementer | Track progress | → `status/in-progress` |
| All sub-issues complete | Close parent | → `status/done` |

### Label conventions

Apply these labels to sub-issues:

- `sub-issue` — identifies it as part of a decomposition
- `size/S`, `size/M`, `size/L` — complexity estimate (don't apply
  `size/XL` — split the sub-issue instead)
- `status/planned` — ready for implementation

Link to the parent via the issue body (the template's `Parent: #<number>`
line). Optionally, add a `parent:<number>` label if your repo's workflow
benefits from label-based filtering.

## Anti-Patterns

Avoid these common planning mistakes:

- **Sub-issues that are just "implement <vague thing>"** — be specific
  about what files to change and what the output looks like.
- **Putting all tests in one sub-issue at the end** — tests should live
  with the implementation they verify.
- **Over-decomposing trivial work** — a 10-line config change doesn't
  need 5 sub-issues. Use judgment.
- **Ignoring existing patterns** — the codebase already has conventions.
  The plan should follow them, not invent new ones.
- **Planning without reading the code** — the codebase map step is not
  optional. Plans based on assumptions instead of actual code lead to
  "code works but doesn't solve the issue" problems.
- **Circular dependencies between sub-issues** — if A depends on B and
  B depends on A, the decomposition is wrong. Merge them or extract
  the shared piece.
