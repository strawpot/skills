---
name: role-creator
description: Create new roles, modify and improve existing roles, and validate role design. Use when users want to create a role from scratch, edit or optimize an existing role, design role dependencies (skills and sub-roles), or plan orchestration patterns for multi-agent delegation. Also use when users mention ROLE.md, agent behavior definitions, or ask about structuring team hierarchies for StrawPot.
---

# Role Creator

A skill for creating new roles and iteratively improving them.

A role is a behavior definition for an agent — it tells the agent who it is, what it does, how it works, and (just as importantly) what it doesn't do. Roles are the atoms of a multi-agent team. Get them right and the team hums; get them wrong and agents step on each other's toes, duplicate work, or sit idle because nobody owns the task.

At a high level, the process goes like this:

- Decide what the role should do, what agent will run it, and how it fits into the team
- Write a draft of the ROLE.md
- Smoke-test the role — walk through example tasks and trace how they'd flow
- Iterate until the role is well-defined and the user is satisfied
- Optionally publish to StrawHub

Your job is to figure out where the user is in this process and help them progress. Maybe they want a role from scratch. Maybe they already have a draft and it's not behaving right. Maybe they're designing a whole team and need help thinking through the structure. Meet them where they are.

## Communicating with the user

Roles involve multi-agent orchestration concepts that may be unfamiliar to some users. Pay attention to context cues:

- Terms like "delegation", "orchestration", and "sub-agent" are fine for technical users
- For less technical users, frame things in team metaphors: "This role is like a team lead who assigns work to specialists"
- Always explain *why* a design decision matters, not just what it is

The people creating roles range from engineers building production agent teams to someone who just wants their AI assistant to behave a certain way. Adjust your depth accordingly — don't over-explain to experts, don't under-explain to newcomers.

---

## StrawPot Documentation Reference

Before creating or improving a role, consult the official StrawPot documentation to ensure compliance with the latest spec. Fetch the relevant pages using WebFetch during the research phase:

- **Roles concept**: `https://docs.strawpot.com/strawhub/concepts/roles` — what a role is, ROLE.md contract, worker vs orchestrator patterns, and how roles compose into teams
- **Skills concept**: `https://docs.strawpot.com/strawhub/concepts/skills` — how roles declare skill dependencies and how agents load them
- **Dependencies**: `https://docs.strawpot.com/strawhub/concepts/dependencies` — declaring dependencies on skills, sub-roles, and MCPs
- **Agents**: `https://docs.strawpot.com/strawhub/concepts/agents` — agent capabilities, tool access, and which agents can run which roles
- **Delegation**: `https://docs.strawpot.com/concepts/delegation` — how orchestrators delegate to sub-agents, task routing, and concurrency patterns
- **Architecture**: `https://docs.strawpot.com/concepts/architecture` — team topologies (hub-and-spoke, layered, peer-to-peer) and isolation boundaries
- **Frontmatter schema**: `https://docs.strawpot.com/strawhub/publishing/frontmatter` — required and optional fields for the `---` block
- **Publishing guide**: `https://docs.strawpot.com/strawhub/publishing/guide` — packaging, versioning, and submission to StrawHub

When drafting or reviewing a ROLE.md, cross-check the frontmatter fields against the schema doc. Verify that the role's delegation assumptions match the delegation and architecture docs. If the role depends on skills or sub-roles, ensure they're declared per the dependencies spec.

## Creating a role

### Capture Intent

Start by understanding what the user needs. Often the conversation already contains clues — maybe they've been manually delegating work between agents, or they've described a team structure, or they said "I need something that handles X." Extract what you can from the conversation first, then fill gaps.

1. **What should this role do?** What is the agent's job when assigned this role?
2. **What are the deliverables?** Code changes, documents, reports, delegated tasks?
3. **What skills does it need?** Skills provide the instructions and workflows the agent follows.
4. **What agent should run it?** Default is `strawpot-claude-code`, but the user might have preferences.

If the user is turning an existing workflow into a role (e.g., "I keep doing this manually, make it a role"), pay close attention to the steps they've been taking, the tools they used, and any corrections they made along the way. That's your blueprint.

### Interview and Research

Probe deeper. As the interview progresses, determine whether this role is a **worker** (does hands-on work) or an **orchestrator** (delegates to other roles). This classification should emerge naturally from the answers — don't force the user to pick upfront.

**For worker roles:**
- What does the workflow look like step by step?
- What should this role explicitly NOT do? (prevents scope creep and overlap)
- Are there existing roles it might overlap with?
- Does it need a skill that doesn't exist yet? If so, that skill needs to be created first — consider using skill-creator.

**For orchestrator roles:**
- What types of tasks will it receive?
- Which sub-roles should it coordinate?
- How should it decide which sub-role to delegate to?
- Should delegation be sequential or parallel?
- How should it aggregate results from sub-roles?
- What happens when no sub-role fits?

**Proactively research the user's existing team.** Read their roles (in `roles/` or `.strawpot/roles/`) to understand the current structure. This helps you avoid overlap, match conventions, and suggest where the new role fits. If they have an orchestrator like `ai-ceo`, think about how the new role will be discovered and routed to.

### Write the ROLE.md

Based on the interview, write the YAML frontmatter and markdown body.

#### Frontmatter Schema

```yaml
---
name: my-role                             # Required: package slug (must match directory name)
description: "What it does and when..."   # Required: one-line summary + trigger contexts
metadata:
  strawpot:
    dependencies:                         # Optional
      skills:                             #   skill dependencies (instructions the agent follows)
        - git-workflow
        - code-review
      roles:                              #   role dependencies (roles it can delegate to)
        - reviewer
        - qa-engineer
    default_agent: strawpot-claude-code   # Optional: default agent runtime
---
```

**Required fields:**

- **name**: Package slug — must be unique within roles and match the directory name.
- **description**: One-line summary of what the role does and when to use it. This is critical — see "Writing Good Descriptions" below.

**Optional fields:**

- **metadata.strawpot.dependencies.skills**: Skills this role depends on. These get staged into the agent's workspace and their instructions are appended to the system prompt. Only include skills the agent actually needs for its work.
- **metadata.strawpot.dependencies.roles**: Roles this role can delegate to. Use `"*"` to depend on all available roles (useful for top-level orchestrators like ai-ceo). For focused orchestrators, list specific roles.
- **metadata.strawpot.default_agent**: The agent runtime to use. Defaults to `strawpot-claude-code` if not specified. Override when a role specifically needs a different runtime.

#### Writing Good Descriptions

The description field is how orchestrators (like `ai-ceo`) decide which role to delegate to. A bad description means tasks get routed to the wrong role — or not routed at all. Think of it as the role's elevator pitch to a routing agent.

**For worker roles**, state the job and list the task types it handles:
```
"Writes code, creates branches, and opens pull requests. Use this role for any task that requires changing source code — features, bug fixes, refactors, or dependency updates."
```

**For orchestrator roles**, say "orchestrator" and "delegates" explicitly so the routing layer knows this role coordinates rather than executes:
```
"Orchestrates comprehensive pull request reviews by delegating to specialized reviewer roles. Use as the entry point for any PR review task."
```

**Common mistakes:**
- Too vague: `"Handles code stuff"` — which code stuff? The router can't distinguish this from other code-related roles.
- Too narrow: `"Reviews Python type annotations in FastAPI endpoints"` — misses 90% of the tasks it should handle.
- Missing the "when to use": `"Code reviewer"` — when should the router pick this over `implementer`? Say it.

#### Role Body Structure

The markdown body becomes the agent's system prompt. Worker roles typically have four sections:

**1. Identity statement** — Who the agent is, in second person. One paragraph. This grounds behavior from the first line.

```markdown
# Implementer

You are a software engineer. You write code, fix bugs, refactor, and
ship pull requests. You are hands-on — you read code, understand it,
change it, and verify it works.
```

**2. "How you work" section** — Numbered steps describing the workflow. Each step explains both *what* to do and *why*. This is the core of the role.

```markdown
## How you work

### 1. Understand the task
Read the task description carefully. Identify what needs to change,
where in the codebase, and why. If genuinely ambiguous, ask for
clarification — but most tasks include enough context.

### 2. Explore the codebase
Before writing any code, read the project's conventions, understand
the architecture, find related tests, check for patterns to follow.
```

**3. Principles** — Guiding rules with bold labels and short explanations that include the *reasoning*.

```markdown
## Principles

- **Read before you write.** Most bugs come from not understanding the
  existing code. Understand first, then change.
- **Small PRs.** One logical change per PR. Easier to review, easier
  to revert.
```

**4. "What you do NOT do" section** — Explicit boundaries. Every "not" should point to who *does* own that work. This section is load-bearing — when an orchestrator sees two roles that could both handle a task, the one with clearer boundaries wins.

```markdown
## What you do NOT do

- You don't decide *what* to build — that comes from the delegator
- You don't review other people's PRs — that's `pr-reviewer`
- You don't triage issues — that's `github-triager`
```

**Orchestrators use different sections.** Instead of "How you work" with numbered steps, orchestrators typically have:

```markdown
## First step: discover your team
Read every ROLE.md in your `roles/` directory.

## Routing
- [Task type A] → `worker-a`
- [Task type B] → `worker-b`

## Writing good task descriptions
Be specific, include context, state the deliverable.

## After delegation completes
Review the result. Summarize for the user.

## What you are not
You are not a [worker type]. Always delegate.
```

The identity statement and "What you are/do not" sections are shared across both types, but the middle sections differ: workers have step-by-step workflows, orchestrators have routing logic and delegation guidance.

#### Inter-role Communication

Roles communicate via **denden** — the built-in protocol for delegation and messaging between agents. When writing orchestrator roles, reference denden explicitly:

- Orchestrators delegate tasks via denden's delegation format
- Workers can ask clarifying questions back to the delegator via denden
- Results flow back through denden when a delegated task completes

Reference it in the body: "Delegate via the denden skill — follow its instructions for the exact delegation format."

### Role Writing Guide

#### Worker vs Orchestrator

**Workers** do the actual work. They depend on skills, produce concrete deliverables, and have detailed step-by-step workflows. Examples: `implementer`, `code-reviewer`, `qa-engineer`, `docs-writer`.

**Orchestrators** route work to other roles. They depend on roles (for delegation targets), focus on task analysis and routing logic, and explicitly state they don't do hands-on work. Examples: `ai-ceo`, `pr-reviewer`.

The reason orchestrators shouldn't do hands-on work isn't a style choice — they carry no skill dependencies, so they lack the specialized context that makes work good. Even a general-purpose worker will outperform an orchestrator at execution. The orchestrator's value is entirely in routing.

Some roles are **hybrid** — they do some work themselves and delegate specific parts. Hybrids are fine, but the split must be obvious. If the agent has to guess whether to do the work or delegate it, the role is poorly designed.

#### How to Think About Writing Roles

1. **Explain the why, not just the what.** LLMs generalize far better from reasoning than from rigid rules. If you find yourself writing ALWAYS or NEVER in all caps, that's a yellow flag. "Don't refactor unrelated code — your PR should be focused so reviewers can assess the change without noise" is better than "You MUST NOT refactor unrelated code." The agent will apply the principle to cases you never explicitly covered.

2. **Keep it lean.** A good role body is 60-140 lines. If you're going longer, consider: should some of this be a skill instead? Should this be two roles? Remove things that aren't pulling their weight — if an instruction doesn't change behavior, it's just noise consuming context.

3. **Match existing patterns.** If the user has existing roles, read them first and match their style. If their `implementer` uses "## How you work" with numbered steps, don't switch to "## Workflow" with bullet points.

4. **Reference skills by name.** When the role depends on a skill, say so in the body: "Follow the `git-workflow` skill for all git operations." This makes the connection between dependency and instruction explicit.

5. **Watch for the extract-to-skill signal.** If you notice the same instructions appearing in multiple roles (e.g., three roles all explain how to write commit messages, or two roles both describe the same testing workflow), that's a strong signal to extract a shared skill. Write it once, put it in a skill, and have the roles depend on it. This keeps roles lean and ensures consistency — when the workflow changes, you update one skill instead of patching five roles.

#### Dependencies Design

- **Skills are for instructions**: If the agent needs to follow a specific workflow (git branching, PR creation, code review checklist), that's a skill dependency.
- **Roles are for delegation**: If the agent needs to hand off work to another specialist, that's a role dependency.
- **Don't over-depend**: Only declare dependencies the role actually uses. Each skill dependency gets appended to the system prompt — extra ones bloat the context and can confuse the agent.
- **Check for transitivity**: If role A depends on role B, and B depends on skill X, role A doesn't need to also depend on skill X (it's resolved transitively).

#### Anti-patterns to Avoid

**The kitchen-sink role.** A role with 10+ skill dependencies that tries to handle everything. If the description says "handles all engineering tasks," it's too broad. Split it.

**The silent orchestrator.** An orchestrator that doesn't explain its routing logic. The agent can't route what it doesn't understand. Always include explicit routing rules: "Bug reports go to `implementer`. Performance issues go to `profiler`."

**The copy-paste role.** A role whose body duplicates instructions from its skill dependencies. If `git-workflow` already explains branching, the role just needs "Follow the `git-workflow` skill" — not a re-explanation.

**Circular delegation.** Role A delegates to role B, which delegates back to A. This creates infinite loops. If you notice the user designing roles that might circularly delegate, flag it immediately.

**The MUST-heavy role.** Every other sentence is "You MUST" or "ALWAYS" or "NEVER." This produces brittle behavior — the agent follows the letter of the rule but misses the spirit. Reframe as principles with reasoning.

### Smoke-test the Role

After writing the draft, validate it with the user. This is the role equivalent of running test cases — lighter than skill evals, but essential.

**1. Read the ROLE.md back** — summarize what the role does, its dependencies, and its boundaries. Make sure you and the user agree on the scope.

**2. Task walkthrough** — come up with 3-5 realistic tasks that might land on this role and trace each one:
- For workers: walk through the workflow step by step. Does each step make sense? Are there gaps?
- For orchestrators: which sub-role would handle each task? Are there tasks that fall through the cracks? Are there tasks where two sub-roles compete?

Share the example tasks with the user: "Here are some scenarios I'd like to walk through. Do these look like realistic things this role would handle?"

Example walkthrough for a worker role:
> Task: "Fix the login bug where emails with '+' return 500"
> → lands on `implementer` → step 1: read task, identify /auth/login → step 2: explore auth module, find email validation → step 3: fix the regex, add test → step 4: open PR. **Verdict: workflow covers this cleanly.**

Example walkthrough for an orchestrator:
> Task: "Review PR #42"
> → lands on `pr-reviewer` → always engage `code-reviewer` → PR touches test files, so also `pr-test-analyzer` → no type changes, skip `type-design-analyzer` → aggregate findings. **Verdict: routing logic works, no gaps.**

**3. Check for overlap** — compare against existing roles. Flag if the new role's scope overlaps with an existing one. Overlap isn't always bad (a focused role can handle a subset better than a generalist), but it should be intentional.

**4. Validate dependencies** — confirm that all referenced skills and roles actually exist (or will be created). Missing dependencies mean the agent gets instructions that reference tools it doesn't have.

**5. Check the "NOT do" section** — make sure every out-of-scope item maps to a specific other role or is explicitly out of the team's scope.

### Iterate

Based on user feedback:

1. Update the ROLE.md
2. Re-review: rerun the task walkthroughs with the changes
3. Repeat until the user is satisfied

Focus improvements on:
- Tightening scope boundaries
- Improving the clarity of the workflow steps
- Making delegation logic more explicit (for orchestrators)
- Ensuring the "what you do NOT do" section is complete

---

## Improving an existing role

When the user wants to improve an existing role, the most important thing is to understand context before changing anything. Read the role, read its neighboring roles, understand the team structure. A change to one role often has implications for others.

### Process

1. **Read the current ROLE.md** — understand what's there
2. **Read related roles and skills** — understand the broader team structure
3. **Ask what's not working** — what behavior needs to change? Get specifics: "it keeps reviewing code instead of delegating" is actionable; "it's not good" isn't
4. **Diagnose the root cause** — the symptom might not point to the right fix (see patterns below)
5. **Make targeted changes** — don't rewrite the whole role unless the user asks for it
6. **Walk through examples** — trace how the changed role would handle the problematic cases

### How to think about improvements

The tricky thing about improving roles is that a behavior problem in one role might actually be caused by a different role (or by the team design itself). An orchestrator that routes tasks to the wrong worker might need better routing logic — or the worker's description might be misleading. A worker that goes out of scope might need a tighter "NOT do" section — or the orchestrator might be sending it tasks it shouldn't get.

So before you change the role, think about whether the fix belongs in this role, in a related role, or in the team structure.

### Common improvement patterns

- **Scope creep**: The role is doing things that belong to another role. Tighten the "NOT do" section and move instructions to the appropriate role. But also check: is the orchestrator sending it tasks it shouldn't get?
- **Unclear delegation**: An orchestrator doesn't have clear routing logic. Add explicit rules for which sub-role handles which type of task. Include examples if the routing is nuanced.
- **Missing dependencies**: The role references a skill or workflow that isn't in its dependencies. Add it — otherwise the agent gets instructions it can't follow.
- **Overly rigid**: Too many MUST/ALWAYS/NEVER constraints. Reframe as principles with reasoning. The agent will generalize better.
- **Context overload**: Too many skill dependencies bloating the prompt. Remove skills the role doesn't actively use. Consider whether some instructions belong in the role body instead.
- **Misrouted tasks**: Tasks keep going to the wrong role. The fix is usually in the description (how the orchestrator discovers roles) or the "NOT do" section (how roles reject out-of-scope work).

---

## Team Design

When a user wants to create multiple related roles (a "team"), help them think through the design holistically. A well-designed team is more than a set of good individual roles — the roles need to fit together.

### Team Patterns

**Hub-and-spoke**: One orchestrator delegates to multiple workers. Simple, clear routing. Best when tasks are cleanly separable.
```
orchestrator → [worker-a, worker-b, worker-c]
```

**Layered**: A top-level orchestrator delegates to sub-orchestrators, each managing their own workers. Best for complex domains with natural groupings.
```
ceo → [pr-reviewer → [code-reviewer, test-analyzer], implementer]
```

**Peer-to-peer**: Workers that can request help from each other (less common, more complex). Only use when workers genuinely need to collaborate on a single task.

### Design Principles

- **Single responsibility**: Each role does one thing well. If you can't describe the role's job in one sentence, it's probably doing too much.
- **Clear boundaries**: If two roles might handle the same task, define explicitly which one owns it. Ambiguity in boundaries is the #1 source of team dysfunction.
- **Fallback path**: Always have a general-purpose role (like `ai-employee`) for tasks that don't fit a specialist. Without a fallback, unroutable tasks just fail.
- **Minimal orchestration**: Don't add an orchestrator unless you have 3+ workers that need routing. With 1-2 workers, direct delegation is simpler and faster.
- **Verify completeness**: After designing all roles, list 10 realistic tasks and trace each one through the team. Every task should have a clear path to a role that can handle it. If tasks fall through the cracks, you have a coverage gap.

---

## Publish to StrawHub (optional)

After the role is finalized, the user can publish it:

```bash
# Authenticate (first time only)
strawhub login

# Publish
strawhub publish role ./my-role

# With version and changelog
strawhub publish role ./my-role --version 1.0.0 --changelog "Initial release"

# With tags
strawhub publish role ./my-role --tag orchestrator --tag devops
```

**Publishing rules:**
- The `name` field in frontmatter must match the package slug
- Versions follow semver (`major.minor.patch`) and must be strictly greater than the latest published
- Dependencies declared in frontmatter are validated — each skill and role slug must exist in the registry
- First publisher of a slug owns it; only the owner can publish new versions
- File constraints: max 20 files per package, max 512 KB per file

Alternatively, publish via the StrawHub web UI at strawhub.dev/upload.

---

## Quick Reference

### Worker Role Template

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

### Orchestrator Role Template

```yaml
---
name: my-orchestrator
description: "Orchestrates X by delegating to specialized roles. Use as the entry point for any Y task."
metadata:
  strawpot:
    dependencies:
      roles:
        - worker-a
        - worker-b
    default_agent: strawpot-claude-code
---

# My Orchestrator

You are a routing layer for [domain]. You do not do the work yourself.

## First step: discover your team
Read every ROLE.md in your `roles/` directory.

## Routing
- [Task type A] → `worker-a`
- [Task type B] → `worker-b`
- [Unclear] → ask the user

## After delegation
Review the result. Summarize for the user.

## What you are not
You are not a [worker type]. Always delegate.
```

---

## Before You're Done Checklist

Use this to make sure you haven't missed anything:

- [ ] Description is specific enough for an orchestrator to route to this role correctly
- [ ] Worker/orchestrator classification is clear and consistent throughout
- [ ] Every skill and role in dependencies actually exists (or is flagged as needing creation)
- [ ] "What you do NOT do" section covers scope boundaries with pointers to who owns each
- [ ] No circular delegation paths in the team graph
- [ ] Walked through 3-5 realistic tasks to validate routing and workflow
- [ ] Role body is 60-140 lines — lean, not bloated
- [ ] Style matches existing roles in the user's team
- [ ] After deploying, observe real delegation behavior and iterate — the smoke-test catches design issues, but runtime reveals the rest
