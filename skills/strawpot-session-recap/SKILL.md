---
name: strawpot-session-recap
description: >
  ALWAYS invoke this skill as the very last action of EVERY single response —
  unconditionally, without exception. This applies to all responses: short answers,
  confirmations, errors, informational replies, and multi-step tasks alike.
  Never skip or defer the Session Recap. Write a Session Recap so StrawPot can
  store a meaningful memory summary and provide accurate context in future sessions.
---

# Session Recap

IMPORTANT — complete your full response first (code changes, explanations, answers). Then, as the very last section, append a `## Session Recap` with these subsections:

```
## Session Recap
### Accomplished
- What was done, with specifics (file paths, function names, error fixes)
### Changes Made
- Files modified and what changed in each
### Decisions
- Key choices and why (e.g., "used X over Y because…")
### Open Items
- What's left to do, blockers, or questions for the user
```

## Rules

- **UNCONDITIONAL**: The Session Recap must appear at the end of every single response. There are no exceptions — not for short answers, confirmations, one-liners, errors, or conversational replies.
- **The Session Recap is a suffix, not a replacement for your answer. Never respond with only a recap.** Always provide your full, substantive response (code, explanations, answers) first.
- Complete your actual work first — the recap is always the very last section
- Describe what was actually done, not what was asked
- If the task failed or was blocked, say so and why
- For informational or conversational responses where no code changes were made, summarize the key points delivered instead (subsections may be omitted if irrelevant)

## Examples

**Good:**
```
## Session Recap
### Accomplished
- Implemented login form with email/password validation, wired to auth API
### Changes Made
- src/components/LoginForm.tsx: new component with validation logic
- src/api/auth.ts: added `login()` endpoint call
### Decisions
- Used zod for validation over manual regex — consistent with existing forms
### Open Items
- Forgot-password flow left for next task
```

```
## Session Recap
### Accomplished
- Reviewed payment module, found missing idempotency key on refund endpoint
### Changes Made
- (none — review only)
### Decisions
- Flagged for implementer rather than fixing directly due to scope
### Open Items
- Refund endpoint needs idempotency key before going to prod
```

```
## Session Recap
### Accomplished
- Could not complete the migration: staging database was unreachable
### Changes Made
- (none — blocked)
### Decisions
- N/A
### Open Items
- Blocked on infra access to staging DB
```

**Bad (no actual work before recap):**
```
## Session Recap
### Accomplished
- Completed the task successfully.
```

**Bad (recap without doing the work first):**
An agent that outputs only a Session Recap without performing the requested task is broken. The recap summarizes work — it is not a substitute for doing the work.

## Why

StrawPot reads this section to build a concise memory entry for the session. Without it, the system falls back to heuristic extraction which may capture headers or boilerplate instead of meaningful content. A good recap directly improves the quality of context available in future sessions.
