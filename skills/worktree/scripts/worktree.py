#!/usr/bin/env python3
"""Worktree management for StrawPot agents.

Usage:
  python worktree.py create --name my-feature [--base main] [--issue 42]
  python worktree.py list

Output: JSON to stdout. Exit code 1 on error.
"""

from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path
from typing import NoReturn

MANIFEST_REL = ".strawpot/worktrees.json"
WORKTREES_DIR_REL = ".strawpot/worktrees"


def _git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the result."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
    )


def _find_repo_root() -> Path:
    """Find the git repository root directory."""
    result = _git("rev-parse", "--show-toplevel")
    if result.returncode != 0:
        _error("Not a git repository (or any parent up to mount point)")
    return Path(result.stdout.strip())


def _output(data: dict) -> None:
    """Write a JSON object to stdout."""
    json.dump(data, sys.stdout, indent=2)
    print()


def _error(message: str) -> NoReturn:
    """Print a JSON error and exit."""
    _output({"error": message})
    sys.exit(1)


def _load_manifest(repo_root: Path) -> dict:
    """Load the worktrees manifest, creating it if it doesn't exist."""
    manifest_path = repo_root / MANIFEST_REL
    if not manifest_path.exists():
        return {"worktrees": {}}
    try:
        with open(manifest_path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        _error(f"Failed to read manifest: {e}")


def _save_manifest(repo_root: Path, manifest: dict) -> None:
    """Save the worktrees manifest."""
    manifest_path = repo_root / MANIFEST_REL
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def _get_current_branch() -> str:
    """Get the current branch name."""
    result = _git("rev-parse", "--abbrev-ref", "HEAD")
    if result.returncode != 0:
        _error("Failed to determine current branch")
    return result.stdout.strip()


def _get_git_worktree_paths() -> set[str]:
    """Get paths of all git worktrees."""
    result = _git("worktree", "list", "--porcelain")
    if result.returncode != 0:
        return set()
    paths = set()
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            paths.add(line[len("worktree "):])
    return paths


def create(name: str, base: str | None = None, issue: int | None = None) -> None:
    """Create a new worktree with a dedicated branch."""
    repo_root = _find_repo_root()
    manifest = _load_manifest(repo_root)

    # Check for duplicate name
    if name in manifest["worktrees"]:
        existing = manifest["worktrees"][name]
        _error(
            f"Worktree '{name}' already exists "
            f"(path: {existing['path']}, status: {existing['status']})"
        )

    # Resolve base branch
    if base is None:
        base = _get_current_branch()
    else:
        # Validate base branch exists
        result = _git("rev-parse", "--verify", base)
        if result.returncode != 0:
            # Try with origin/ prefix
            result = _git("rev-parse", "--verify", f"origin/{base}")
            if result.returncode != 0:
                _error(f"Base branch '{base}' does not exist")

    # Paths
    worktree_path = repo_root / WORKTREES_DIR_REL / name
    branch_name = f"worktree/{name}"

    # Ensure parent directory exists
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    # Create the worktree with a new branch
    result = _git("worktree", "add", "-b", branch_name, str(worktree_path), base)
    if result.returncode != 0:
        _error(f"Failed to create worktree: {result.stderr.strip()}")

    # Record in manifest
    rel_path = str(worktree_path.relative_to(repo_root))
    entry = {
        "path": rel_path,
        "branch": branch_name,
        "base_branch": base,
        "issue": issue,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "status": "active",
    }
    manifest["worktrees"][name] = entry
    _save_manifest(repo_root, manifest)

    _output({
        "status": "created",
        "name": name,
        "path": rel_path,
        "branch": branch_name,
        "base_branch": base,
        "issue": issue,
    })


def list_worktrees() -> None:
    """List all tracked worktrees and their status."""
    repo_root = _find_repo_root()
    manifest = _load_manifest(repo_root)

    # Get actual git worktree paths for cross-referencing
    git_worktree_paths = _get_git_worktree_paths()

    worktrees = []
    for name, entry in manifest.get("worktrees", {}).items():
        abs_path = str(repo_root / entry["path"])
        # Determine status: if manifest says active but worktree is gone, it's stale
        status = entry.get("status", "active")
        if status == "active" and abs_path not in git_worktree_paths:
            status = "stale"

        worktrees.append({
            "name": name,
            "path": entry["path"],
            "branch": entry["branch"],
            "base_branch": entry.get("base_branch", "unknown"),
            "issue": entry.get("issue"),
            "created_at": entry.get("created_at"),
            "status": status,
        })

    _output({"worktrees": worktrees})


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Worktree management for StrawPot agents."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    create_parser = subparsers.add_parser("create", help="Create a new worktree")
    create_parser.add_argument(
        "--name", required=True, help="Worktree name (used in path and branch)"
    )
    create_parser.add_argument(
        "--base", default=None, help="Base branch to create from (default: current branch)"
    )
    create_parser.add_argument(
        "--issue", type=int, default=None, help="Issue number to link"
    )

    # list
    subparsers.add_parser("list", help="List all tracked worktrees")

    args = parser.parse_args()

    if args.command == "create":
        create(name=args.name, base=args.base, issue=args.issue)
    elif args.command == "list":
        list_worktrees()


if __name__ == "__main__":
    main()
