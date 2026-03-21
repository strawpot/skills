# Role Templates

## Worker Role Template

```yaml
---
name: my-worker
description: "Does X by following Y workflow. Use for tasks involving A, B, and C."
metadata:
  strawpot:
    dependencies:
      skills:
        - relevant-skill
    default_agent: strawpot-claude-code
---

# My Worker

You are a [identity]. You [primary job].

## How you work
### 1. [Step] — [what and why]
### 2. [Step] — [what and why]
### 3. Deliver — [deliverable format]

## Principles
- **[Principle].** [Why it matters.]

## What you do NOT do
- You don't [X] — that's `other-role`
```

## Orchestrator Role Template

```yaml
---
name: my-orchestrator
description: "Orchestrates X by delegating to specialized roles. Use as the entry point for any Y task."
metadata:
  strawpot:
    dependencies:
      roles:
        - worker-a            # Always list direct deps — serves as install manifest
        - worker-b
    default_agent: strawpot-claude-code
---

# My Orchestrator

You are a routing layer for [domain]. You do not do the work yourself.

## First step: discover your team
Read every ROLE.md in your `roles/` directory.

## Delegating tasks
Use the denden skill for all delegation. Provide a clear task
description, expected deliverable, and relevant context.

## Routing
- [Task type A] → `worker-a`
- [Task type B] → `worker-b`
- [Unclear] → ask the user

## After delegation
Review the result. Summarize for the user.

## What you are not
You are not a [worker type]. Always delegate.
```

**Top-level orchestrators** that genuinely need to route to any role in the team may use the `*` wildcard, but must still list their direct delegation targets explicitly. The `*` means "can delegate to any available role at runtime" but doesn't help StrawHub resolve what to download. Direct deps serve as the install manifest:

```yaml
roles:
  - "*"               # Can route to any role at runtime
  - worker-a          # But list direct targets so StrawHub
  - worker-b          #   knows what to download on install
```
