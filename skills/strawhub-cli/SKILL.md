---
name: strawhub-cli
description: StrawHub package management for roles, skills, agents, and memories
metadata:
  strawpot:
    tools:
      strawhub:
        description: StrawHub CLI
        install:
          macos: pip install strawhub
          linux: pip install strawhub
---

# StrawHub CLI

StrawHub is the package registry for StrawPot resources.

## Search Packages

```bash
# Search all resource types
strawhub search "github"

# Search by type
strawhub search --type skill "git"
strawhub search --type role "engineer"
strawhub search --type agent "claude"
## Install Packages

```bash
# Install globally
strawhub install skill git-workflow
strawhub install role implementer

# Install to a specific project
strawhub install skill git-workflow --project /path/to/project

# Install a specific version
strawhub install skill git-workflow@1.2.0
```

## View Package Info

```bash
strawhub info skill git-workflow
strawhub info role implementer
```

## List Installed

```bash
# List all globally installed
strawhub list

# List by type
strawhub list --type skill
strawhub list --type role

# List project-scoped
strawhub list --project /path/to/project
```

## Uninstall

```bash
strawhub uninstall skill git-workflow
strawhub uninstall role implementer --project /path/to/project
```
```
