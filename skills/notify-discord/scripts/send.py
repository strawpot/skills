#!/usr/bin/env python3
"""
Send a message to a Discord channel via webhook.

Usage:
  python send.py "Hello world"
  python send.py --webhook-url "https://discord.com/api/webhooks/..." "Hello world"
  python send.py --username "StrawPot Bot" "Hello world"

Environment variables:
  DISCORD_WEBHOOK_URL (required) Webhook URL from Discord channel settings

Output: JSON response to stdout (empty on success). Exit code 1 on error.
"""

import json
import os
import sys
import urllib.request


MAX_MESSAGE_LENGTH = 2000


def send_message(
    webhook_url: str,
    content: str,
    username: str | None = None,
) -> list[dict]:
    """Send a message, chunking if it exceeds Discord's limit."""
    chunks = []
    while content:
        chunk = content[:MAX_MESSAGE_LENGTH]
        content = content[MAX_MESSAGE_LENGTH:]
        chunks.append(chunk)

    results = []
    for chunk in chunks:
        payload: dict = {"content": chunk}
        if username:
            payload["username"] = username

        data = json.dumps(payload).encode()
        # Append ?wait=true to get a response body
        url = webhook_url
        if "?" in url:
            url += "&wait=true"
        else:
            url += "?wait=true"

        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode()
                result = json.loads(body) if body else {"ok": True}
                results.append(result)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            try:
                error_json = json.loads(error_body)
            except json.JSONDecodeError:
                error_json = {"error": error_body}
            results.append({"ok": False, "status": e.code, **error_json})

    return results


def main():
    args = sys.argv[1:]

    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    username = None
    message_parts = []

    i = 0
    while i < len(args):
        if args[i] == "--webhook-url" and i + 1 < len(args):
            webhook_url = args[i + 1]
            i += 2
        elif args[i] == "--username" and i + 1 < len(args):
            username = args[i + 1]
            i += 2
        else:
            message_parts.append(args[i])
            i += 1

    message = " ".join(message_parts)

    if not message:
        print("Error: message is required", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if not webhook_url:
        print(
            "Error: webhook URL is required (use --webhook-url or set DISCORD_WEBHOOK_URL)",
            file=sys.stderr,
        )
        sys.exit(1)

    results = send_message(webhook_url, message, username)

    if len(results) == 1:
        print(json.dumps(results[0], indent=2))
    else:
        print(json.dumps(results, indent=2))

    if any(not r.get("ok", True) and r.get("status", 0) >= 400 for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
