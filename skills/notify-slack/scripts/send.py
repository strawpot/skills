#!/usr/bin/env python3
"""
Send a message to a Slack channel via the Web API.

Usage:
  python send.py "Hello world"
  python send.py --channel "C0123456789" "Hello world"
  python send.py --channel "C0123456789" --thread-ts "1234567890.123456" "Thread reply"

Environment variables:
  SLACK_BOT_TOKEN      (required) Bot token (xoxb-...)
  SLACK_DEFAULT_CHANNEL (optional) Default channel ID if --channel not given

Output: JSON response to stdout. Exit code 1 on error.
"""

import json
import os
import sys
import urllib.request


MAX_MESSAGE_LENGTH = 3900


def send_message(
    token: str,
    channel: str,
    text: str,
    thread_ts: str | None = None,
) -> list[dict]:
    """Send a message, chunking if it exceeds safe limits."""
    chunks = []
    while text:
        chunk = text[:MAX_MESSAGE_LENGTH]
        text = text[MAX_MESSAGE_LENGTH:]
        chunks.append(chunk)

    results = []
    for chunk in chunks:
        payload: dict = {
            "channel": channel,
            "text": chunk,
        }
        if thread_ts:
            payload["thread_ts"] = thread_ts

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=data,
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read().decode())
                results.append(result)
                # Use the first message's ts for threading subsequent chunks
                if not thread_ts and result.get("ok") and result.get("ts"):
                    thread_ts = result["ts"]
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

    channel = os.environ.get("SLACK_DEFAULT_CHANNEL")
    thread_ts = None
    message_parts = []

    i = 0
    while i < len(args):
        if args[i] == "--channel" and i + 1 < len(args):
            channel = args[i + 1]
            i += 2
        elif args[i] == "--thread-ts" and i + 1 < len(args):
            thread_ts = args[i + 1]
            i += 2
        else:
            message_parts.append(args[i])
            i += 1

    message = " ".join(message_parts)

    if not message:
        print("Error: message is required", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("Error: SLACK_BOT_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not channel:
        print(
            "Error: channel is required (use --channel or set SLACK_DEFAULT_CHANNEL)",
            file=sys.stderr,
        )
        sys.exit(1)

    results = send_message(token, channel, message, thread_ts)

    if len(results) == 1:
        print(json.dumps(results[0], indent=2))
    else:
        print(json.dumps(results, indent=2))

    if any(not r.get("ok", True) for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
