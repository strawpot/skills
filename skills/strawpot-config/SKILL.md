---
name: strawpot-config
description: StrawPot configuration management
---

# StrawPot Configuration

## Config Locations

- **Global**: `~/.strawpot/strawpot.toml` — applies to all projects
- **Project**: `<project>/strawpot.toml` — overrides global settings

## Config Sections

```toml
# Default agent runtime
runtime = "strawpot-claude-code"

# Isolation mode: "none" or "worktree"
isolation = "none"

# Orchestrator settings
orchestrator_role = "orchestrator"
permission_mode = "default"

# Delegation policy
max_depth = 3
agent_timeout = 600  # seconds, optional
max_delegate_retries = 0

# Memory provider
memory = "dial"

# Merge strategy: "auto", "local", "pr"
merge_strategy = "auto"

# Agent-specific config
[agents.strawpot-claude-code]
model = "claude-opus-4-6"

# Skill environment variables
[skills.github-issues.env]
GITHUB_TOKEN = "ghp_..."
## Editing Config

Use a text editor or `strawpot config` subcommands. Changes to global
config affect all future sessions. Changes to project config only affect
that project.

When editing TOML files, preserve existing comments and formatting.
Only modify the specific fields requested.
```
