---
name: self-improvement
description: "Iterative self-evaluation loop via self-delegation. After completing work, the agent delegates to its own role for an independent evaluation pass, incorporates feedback, and repeats until no further improvements are found. Use this skill when the user wants higher-quality output through self-review, when a task benefits from multiple refinement passes, or when the user mentions self-improvement, self-review, iterative refinement, or polishing output."
---

# Self-Improvement

This skill enables an agent to iteratively improve its own work by delegating to a fresh instance of itself for evaluation. Each evaluation pass runs in a clean context — the evaluator sees only the output, not the original reasoning — which catches blind spots the author misses.

## How it works

1. Complete the task as normal
2. Delegate to your own role via denden, asking the new instance to evaluate your output
3. Read the evaluation feedback
4. If improvements are needed, apply them and repeat from step 2
5. If no improvements are needed, deliver the final output

The depth limit (`max_depth`) naturally caps the number of iterations. This is the safety mechanism — you don't need to count iterations yourself.

## Prerequisites

Self-delegation is built into denden. Set `delegateTo` to an empty string `""` and the orchestrator resolves it to your own role automatically. Alternatively, your role slug is available in the `$STRAWPOT_ROLE` environment variable. No special role dependency declaration is needed.

## The evaluation loop

### Step 1: Complete the task

Do your work normally. Produce your output — code, document, analysis, whatever the task requires. Save or stage the output so it can be passed to the evaluator.

### Step 2: Delegate to yourself for evaluation

Use denden to delegate to your own role. The task description should contain:
- The **original task** the user asked for (so the evaluator has context)
- Your **complete output** (so the evaluator can assess it)
- Clear instruction that this is an **evaluation pass**, not a new task

Use `delegateTo: ""` (empty string) for self-delegation. The orchestrator resolves it to your own role automatically. Structure the task text like this:

```
## Evaluation request

You are evaluating work produced by a previous instance of your role.
Do NOT redo the task. Instead, review the output critically and provide
specific, actionable feedback.

### Original task
{paste the original task here}

### Output to evaluate
{paste the complete output here}

### Instructions
Review the output against the original task. For each issue found:
1. State what is wrong or could be improved
2. Explain why it matters
3. Suggest the specific fix

If the output fully satisfies the task with no meaningful improvements
possible, respond with exactly: NO_FURTHER_IMPROVEMENTS

Do not suggest cosmetic changes, style preferences, or improvements
beyond the task scope. Only flag issues that would materially affect
the quality or correctness of the output.
```

Send via denden:

```bash
denden send '{"delegate":{"delegateTo":"","task":{"text":"<evaluation prompt above>","returnFormat":"TEXT"}}}'
```

### Step 3: Process the feedback

Read `delegateResult.text` from the denden response. Check:
- Contains `NO_FURTHER_IMPROVEMENTS` — you're done, deliver the output
- Contains specific feedback — apply the improvements and go back to step 2
- Delegation fails with `DENY_DEPTH_LIMIT` — you've hit the iteration cap, deliver your best output so far

### Step 4: Apply improvements and repeat

Incorporate the feedback into your output. Then delegate again for another evaluation pass. Each pass should produce fewer issues until the evaluator finds nothing left to improve.

## Termination conditions

The loop ends when any of these occur:

1. **Evaluator says done** — responds with `NO_FURTHER_IMPROVEMENTS`
2. **Depth limit reached** — denden returns `DENY_DEPTH_LIMIT`, meaning you've exhausted your iteration budget
3. **Diminishing returns** — the evaluator keeps suggesting the same changes, indicating you're going in circles

When terminated by depth limit, don't treat it as a failure — deliver your current output. Multiple passes have already improved it.

## Writing good evaluation prompts

The quality of the evaluation depends on the prompt you send to the evaluator. Key principles:

- **Include the original task.** Without it, the evaluator can't judge whether the output is correct — only whether it looks nice.
- **Include the complete output.** Partial output leads to partial reviews.
- **Say "evaluation, not execution."** Without this, the evaluator might redo the work instead of reviewing it.
- **Set a quality bar.** "Only flag issues that materially affect quality" prevents the evaluator from nitpicking endlessly.
- **Use the sentinel.** `NO_FURTHER_IMPROVEMENTS` gives you a clean termination signal to parse.

## When to use this skill

Use self-improvement when:
- The task has objective quality criteria (code correctness, spec compliance, completeness)
- The output is complex enough that a single pass might miss issues
- The user explicitly asks for high-quality or polished output

Don't use it when:
- The task is simple and a single pass is sufficient
- The output is subjective (creative writing, art) — self-evaluation tends to homogenize
- You're already at depth limit from prior delegations
- Speed matters more than polish

## Depth budget awareness

Each self-improvement iteration consumes one level of delegation depth. If the default `max_depth` is 3 and you're already at depth 1 (delegated by an orchestrator), you have 2 iterations available. Plan accordingly:

- At depth 0 (top-level): up to `max_depth` iterations
- At depth N: up to `max_depth - N` iterations remaining

If only 1 iteration remains, make it count — ask the evaluator to focus on the most critical issues only.
