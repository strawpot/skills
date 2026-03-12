---
name: strawpot-session-recap
description: Write a Session Recap at the end of every response so strawpot can store a meaningful memory summary and provide accurate context in future sessions.
---

# Session Recap

At the end of **every response**, append a `## Session Recap` section:

```
## Session Recap
<one or two sentences: what you accomplished and any key outcome or decision>
```

## Rules

- Always include it, even for short or simple tasks
- One or two sentences maximum — no bullet lists, no markdown formatting inside the recap
- Describe what was actually done, not what was asked
- If the task failed or was blocked, say so and why

## Examples

**Good:**
```
## Session Recap
Implemented the login form with email/password validation and wired it to the auth API. Left the forgot-password flow for the next task.
```

```
## Session Recap
Reviewed the payment module — found a missing idempotency key on the refund endpoint and flagged it for the implementer.
```

```
## Session Recap
Could not complete the migration: the staging database was unreachable. Blocked on infra access.
```

**Bad (too vague):**
```
## Session Recap
Completed the task successfully.
```

**Bad (markdown inside recap):**
```
## Session Recap
- Fixed bug in auth
- Updated tests
```

## Why

StrawPot reads this section to build a concise memory entry for the session. Without it, the system falls back to heuristic extraction which may capture headers or boilerplate instead of meaningful content. A good recap directly improves the quality of context available in future sessions.
