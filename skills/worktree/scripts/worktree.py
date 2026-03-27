#!/usr/bin/env python3
"""Worktree management for StrawPot agents.

Usage:
  python worktree.py create --name my-feature [--base main] [--issue 42]
  python worktree.py list
  python worktree.py merge --name my-feature
  python worktree.py discard --name my-feature [--keep-remote]

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
PATCHES_DIR_REL = ".strawpot/patches"


def _git(
    *args: str,
    cwd: str | Path | None = None,
    input_data: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the result."""
    try:
        return subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=cwd,
            input=input_data,
        )
    except FileNotFoundError:
        _error("git is not installed or not on PATH")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a command and return the result."""
    return subprocess.run(args, capture_output=True, text=True, timeout=15)


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
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        _error(f"Failed to read manifest: {e}")
    if not isinstance(data, dict) or "worktrees" not in data:
        _error("Invalid manifest format: missing 'worktrees' key")
    return data


def _save_manifest(repo_root: Path, manifest: dict) -> None:
    """Save the worktrees manifest."""
    manifest_path = repo_root / MANIFEST_REL
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
    except OSError as e:
        _error(f"Failed to save manifest: {e}")


def _get_current_branch() -> str:
    """Get the current branch name."""
    result = _git("rev-parse", "--abbrev-ref", "HEAD")
    if result.returncode != 0:
        _error("Failed to determine current branch")
    branch = result.stdout.strip()
    if branch == "HEAD":
        _error("Cannot create worktree from detached HEAD — use --base to specify a branch")
    return branch


def _get_git_worktree_paths() -> set[str]:
    """Get paths of all git worktrees."""
    result = _git("worktree", "list", "--porcelain")
    if result.returncode != 0:
        _error(f"Failed to list git worktrees: {result.stderr.strip()}")
    paths = set()
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            paths.add(line[len("worktree "):])
    return paths


def _get_manifest_entry(manifest: dict, name: str) -> dict:
    """Get a worktree entry from the manifest, or error if not found."""
    if name not in manifest["worktrees"]:
        _error(f"Worktree '{name}' not found in manifest")
    return manifest["worktrees"][name]


def _detect_pr(branch: str) -> dict | None:
    """Check if a PR exists for the given branch. Returns PR info or None."""
    try:
        result = _run("gh", "pr", "list", "--head", branch, "--json", "url,state", "--limit", "1")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        prs = json.loads(result.stdout)
        return prs[0] if prs else None
    except (json.JSONDecodeError, IndexError):
        return None


def _remove_worktree(repo_root: Path, entry: dict) -> None:
    """Remove a git worktree, tolerating already-removed state."""
    worktree_path = repo_root / entry["path"]
    if worktree_path.exists():
        _git("worktree", "remove", str(worktree_path), "--force")
    # Prune to clean up stale worktree references
    _git("worktree", "prune")


def _delete_local_branch(branch: str) -> bool:
    """Delete a local branch. Returns True if deleted."""
    result = _git("branch", "-D", branch)
    return result.returncode == 0


def _delete_remote_branch(branch: str) -> bool:
    """Delete a remote branch. Returns True if deleted."""
    result = _git("push", "origin", "--delete", branch)
    return result.returncode == 0


def create(name: str, base: str | None = None, issue: int | None = None) -> None:
    """Create a new worktree with a dedicated branch."""
    repo_root = _find_repo_root()
    manifest = _load_manifest(repo_root)

    if name in manifest["worktrees"]:
        existing = manifest["worktrees"][name]
        _error(
            f"Worktree '{name}' already exists "
            f"(path: {existing['path']}, status: {existing['status']})"
        )

    if base is None:
        base = _get_current_branch()
    else:
        result = _git("rev-parse", "--verify", base)
        if result.returncode != 0:
            result = _git("rev-parse", "--verify", f"origin/{base}")
            if result.returncode != 0:
                _error(f"Base branch '{base}' does not exist")
            base = f"origin/{base}"

    worktree_path = repo_root / WORKTREES_DIR_REL / name
    branch_name = f"worktree/{name}"

    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    result = _git("worktree", "add", "-b", branch_name, str(worktree_path), base)
    if result.returncode != 0:
        _error(f"Failed to create worktree: {result.stderr.strip()}")

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

    try:
        _save_manifest(repo_root, manifest)
    except SystemExit:
        _git("worktree", "remove", str(worktree_path), "--force")
        _git("branch", "-D", branch_name)
        raise

    _output({
        "status": "created",
        "name": name,
        "path": rel_path,
        "branch": branch_name,
        "base_branch": base,
        "issue": issue,
    })


def merge(name: str) -> None:
    """Merge worktree changes back to the base branch and clean up."""
    repo_root = _find_repo_root()
    manifest = _load_manifest(repo_root)
    entry = _get_manifest_entry(manifest, name)
    branch = entry["branch"]
    base_branch = entry.get("base_branch", "main")

    # Check for PR
    pr = _detect_pr(branch)

    if pr and pr.get("state") == "MERGED":
        # PR already merged — full cleanup
        _remove_worktree(repo_root, entry)
        _delete_local_branch(branch)
        entry["status"] = "done"
        _save_manifest(repo_root, manifest)
        _output({
            "status": "done",
            "name": name,
            "message": "PR merged — worktree and branch cleaned up",
            "pr_url": pr.get("url"),
        })
        return

    if pr and pr.get("state") == "OPEN":
        # PR is open — remove worktree but keep the branch
        _remove_worktree(repo_root, entry)
        entry["status"] = "merged-via-pr"
        _save_manifest(repo_root, manifest)
        _output({
            "status": "merged-via-pr",
            "name": name,
            "message": "PR is open — worktree removed, branch preserved for PR",
            "pr_url": pr.get("url"),
            "branch": branch,
        })
        return

    # No PR — apply diff to base as unstaged changes
    diff_result = _git("diff", f"{base_branch}..{branch}")
    if diff_result.returncode != 0:
        _error(f"Failed to generate diff: {diff_result.stderr.strip()}")

    patch = diff_result.stdout
    if not patch.strip():
        _remove_worktree(repo_root, entry)
        _delete_local_branch(branch)
        entry["status"] = "merged"
        _save_manifest(repo_root, manifest)
        _output({
            "status": "merged",
            "name": name,
            "message": "No changes to merge — worktree cleaned up",
        })
        return

    # Dry-run check for conflicts
    check_result = _git("apply", "--check", input_data=patch)
    if check_result.returncode != 0:
        # Conflict — save patch file for recovery
        patches_dir = repo_root / PATCHES_DIR_REL
        patches_dir.mkdir(parents=True, exist_ok=True)
        patch_path = patches_dir / f"{name}.patch"
        patch_path.write_text(patch, encoding="utf-8")

        entry["status"] = "conflict"
        _save_manifest(repo_root, manifest)
        _output({
            "status": "conflict",
            "name": name,
            "message": "Merge conflict detected — patch saved for manual resolution",
            "patch_path": str(patch_path.relative_to(repo_root)),
            "conflict_details": check_result.stderr.strip(),
        })
        return

    # Clean apply
    apply_result = _git("apply", input_data=patch)
    if apply_result.returncode != 0:
        _error(f"Failed to apply patch: {apply_result.stderr.strip()}")

    _remove_worktree(repo_root, entry)
    _delete_local_branch(branch)
    entry["status"] = "merged"
    _save_manifest(repo_root, manifest)
    _output({
        "status": "merged",
        "name": name,
        "message": "Changes applied as unstaged modifications",
    })


def discard(name: str, keep_remote: bool = False) -> None:
    """Discard worktree and branch without merging."""
    repo_root = _find_repo_root()
    manifest = _load_manifest(repo_root)
    entry = _get_manifest_entry(manifest, name)
    branch = entry["branch"]

    _remove_worktree(repo_root, entry)
    _delete_local_branch(branch)

    if not keep_remote:
        _delete_remote_branch(branch)

    entry["status"] = "discarded"
    _save_manifest(repo_root, manifest)
    _output({
        "status": "discarded",
        "name": name,
        "message": "Worktree and branch removed",
        "remote_deleted": not keep_remote,
    })


def list_worktrees() -> None:
    """List all tracked worktrees and their status."""
    repo_root = _find_repo_root()
    manifest = _load_manifest(repo_root)
    git_worktree_paths = _get_git_worktree_paths()

    worktrees = []
    for name, entry in manifest.get("worktrees", {}).items():
        abs_path = str(repo_root / entry["path"])
        status = entry.get("status", "active")
        if status == "active" and abs_path not in git_worktree_paths:
            status = "stale"

        worktrees.append({
            "name": name,
            "path": entry["path"],
            "branch": entry["branch"],
            "base_branch": entry.get("base_branch"),
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

    merge_parser = subparsers.add_parser("merge", help="Merge worktree changes back")
    merge_parser.add_argument(
        "--name", required=True, help="Worktree name to merge"
    )

    discard_parser = subparsers.add_parser("discard", help="Discard worktree without merging")
    discard_parser.add_argument(
        "--name", required=True, help="Worktree name to discard"
    )
    discard_parser.add_argument(
        "--keep-remote", action="store_true", default=False,
        help="Preserve remote branch"
    )

    subparsers.add_parser("list", help="List all tracked worktrees")

    args = parser.parse_args()

    if args.command == "create":
        create(name=args.name, base=args.base, issue=args.issue)
    elif args.command == "merge":
        merge(name=args.name)
    elif args.command == "discard":
        discard(name=args.name, keep_remote=args.keep_remote)
    elif args.command == "list":
        list_worktrees()


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        _error(f"Unexpected error: {e}")
