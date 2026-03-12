---
name: strawpot-docs
description: Fetch the latest StrawPot and StrawHub documentation from the web
metadata:
  strawpot:
    tools:
      curl:
        description: HTTP client for fetching documentation pages
        install:
          linux: apt install curl
---

# StrawPot Documentation

The official StrawPot documentation is at **https://docs.strawpot.com**.
Fetch any page to get the latest information — documentation is updated
with each release.

## Fetch a Documentation Page

```bash
curl -s https://docs.strawpot.com/{page}
```

Or use your built-in WebFetch tool with the URL directly.

## Available Pages

### Get Started
- `https://docs.strawpot.com` — Overview and introduction
- `https://docs.strawpot.com/quickstart` — Installation and first session

### Concepts
- `https://docs.strawpot.com/concepts/architecture` — How StrawPot works
- `https://docs.strawpot.com/concepts/sessions` — Session lifecycle
- `https://docs.strawpot.com/concepts/delegation` — Agent delegation model
- `https://docs.strawpot.com/concepts/isolation` — Session isolation
- `https://docs.strawpot.com/concepts/memory` — Memory providers

### CLI Reference
- `https://docs.strawpot.com/cli/commands` — All CLI commands and flags
- `https://docs.strawpot.com/cli/configuration` — strawpot.toml reference

### Agents
- `https://docs.strawpot.com/agents/overview` — Agent system overview
- `https://docs.strawpot.com/agents/claude-code` — Claude Code agent setup

### Web Dashboard (GUI)
- `https://docs.strawpot.com/gui` — Dashboard overview
- `https://docs.strawpot.com/gui/quickstart` — Getting started with the GUI
- `https://docs.strawpot.com/gui/scheduled-tasks` — Scheduled tasks guide

### StrawHub (Resource Registry)
- `https://docs.strawpot.com/strawhub` — StrawHub overview
- `https://docs.strawpot.com/strawhub/quickstart` — Installing resources
- `https://docs.strawpot.com/strawhub/concepts/skills` — Skills
- `https://docs.strawpot.com/strawhub/concepts/roles` — Roles
- `https://docs.strawpot.com/strawhub/concepts/agents` — Agents
- `https://docs.strawpot.com/strawhub/concepts/memories` — Memory providers
- `https://docs.strawpot.com/strawhub/concepts/dependencies` — Dependencies
- `https://docs.strawpot.com/strawhub/cli/commands` — strawhub CLI reference
- `https://docs.strawpot.com/strawhub/publishing/guide` — Publishing resources
- `https://docs.strawpot.com/strawhub/publishing/frontmatter` — Frontmatter reference
- `https://docs.strawpot.com/strawhub/api/reference` — StrawHub API reference

## When to Use This Skill

- A user asks about a feature you are unsure of — fetch the relevant page
- You need the exact flags for a CLI command — fetch `cli/commands`
- A user reports unexpected behavior — fetch the relevant concept page to verify expected behavior
- You need to know what fields a `strawpot.toml` key accepts — fetch `cli/configuration`
