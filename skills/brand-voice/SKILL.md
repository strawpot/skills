---
name: brand-voice
description: "Brand voice guidelines and tone consistency for all public-facing content. Provides rules for evaluating and adjusting content tone, style, and messaging. Use this skill whenever creating, reviewing, or editing marketing content, social media posts, documentation, or any public communications to ensure brand consistency."
---

# Brand Voice

Guidelines and tools for maintaining consistent brand voice across all content and channels. This skill helps marketers, writers, and content creators produce on-brand content and evaluate drafts for tone consistency.

## Workspace configuration

The primary source of brand voice rules is the **`brand-voice.md`** file in the workspace root. Always read this file before creating or reviewing any content. If it does not exist, ask the user to provide brand voice direction before proceeding.

A well-structured `brand-voice.md` should contain:

- **Brand personality** — 3-5 adjectives that define the brand's character
- **Target audience** — Who you are writing for
- **Tone spectrum** — Where the brand falls on scales like formal/casual, serious/playful, technical/accessible
- **Messaging pillars** — Core themes and value propositions to emphasize
- **Vocabulary** — Preferred terms and terms to avoid
- **Examples** — Good and bad examples of on-brand vs. off-brand content

## Content review checklist

When reviewing any piece of content for brand consistency, evaluate against these criteria:

### 1. Tone alignment

- Does it match the personality adjectives in `brand-voice.md`?
- Is the formality level appropriate for the platform and audience?
- Does it sound like the same voice as other recent posts?

### 2. Messaging alignment

- Does it reinforce at least one messaging pillar?
- Does it accurately represent the product/brand?
- Are claims substantiated and not overpromising?

### 3. Vocabulary check

- Are preferred terms used consistently?
- Are banned or discouraged terms avoided?
- Is jargon used appropriately for the target audience?

### 4. Platform adaptation

The core voice stays the same — only the expression adapts to the platform. Platform-specific guidelines live in each platform's dedicated marketer role. This keeps brand-voice universal and platform-agnostic.

General guidance:

| Context | Adaptation |
|---|---|
| Blog | Thorough, educational. Can be more detailed and technical. |
| Documentation | Clear, precise, neutral. Minimize personality, maximize clarity. |
| Social media | See the dedicated marketer role for each platform. |

### 5. Guardrails

Content must never:
- Make claims that cannot be backed up
- Use superlatives without evidence ("best", "fastest", "only")
- Disparage competitors by name
- Include controversial political, religious, or social commentary
- Promise features or timelines that are not confirmed
- Use manipulative urgency ("Act now!", "Limited time!")
- Misrepresent the product's capabilities

## Evaluating a draft

When asked to review content for brand voice, provide structured feedback:

```
## Brand Voice Review

**Overall alignment**: [Strong / Moderate / Weak]

**Tone**: [Assessment — e.g., "Too formal for Twitter; needs to be more conversational"]

**Messaging**: [Assessment — e.g., "Reinforces the 'developer productivity' pillar effectively"]

**Vocabulary**: [Assessment — e.g., "Uses 'simple' which is a discouraged term; suggest 'straightforward' instead"]

**Platform fit**: [Assessment — e.g., "Good length for LinkedIn; would need to be shortened for Twitter"]

**Suggested revision**: [Revised version if changes are needed]
```

## Creating on-brand content

When creating new content, follow this process:

1. **Read `brand-voice.md`** from the workspace root
2. **Identify the platform** and adapt the voice accordingly
3. **Choose a messaging pillar** to anchor the content
4. **Draft the content** using preferred vocabulary and appropriate tone
5. **Self-review** against the checklist above before presenting
6. **Present the draft** with a brief note on which pillar it targets and any brand voice considerations

## Consistency across roles

All marketing roles share the same brand voice but adapt it for their platform. To maintain consistency:

- All roles read the same `brand-voice.md` file
- All roles log content to the content-calendar, making it possible to review voice consistency across channels
- When adapting content from one platform to another, preserve the core message and tone while adjusting format and length
- Periodically review recent posts across all platforms to ensure voice drift has not occurred

## Updating brand voice

If the user updates `brand-voice.md`, all subsequent content should reflect the changes immediately. There is no caching — always read the file fresh before creating content.

When the user asks to evolve the brand voice:
1. Discuss what aspects to change and why
2. Draft updates to `brand-voice.md`
3. Present before/after examples showing how content would differ
4. Get explicit approval before writing the updated file
