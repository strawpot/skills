#!/usr/bin/env python3
"""
Send a message to a Telegram chat via the Bot API.

Usage:
  python send.py "Hello world"
  python send.py --chat-id "-100123456789" "Hello world"
  python send.py --parse-mode MarkdownV2 "**Bold** text"

Environment variables:
  TELEGRAM_BOT_TOKEN       (required) Bot API token from @BotFather
  TELEGRAM_DEFAULT_CHAT_ID (optional) Default chat ID if --chat-id not given

Output: JSON response to stdout. Exit code 1 on error.
"""

import json
import os
import sys
import urllib.parse
import urllib.request


MAX_MESSAGE_LENGTH = 4096


def send_message(token: str, chat_id: str, text: str, parse_mode: str | None = None) -> list[dict]:
    """Send a message, chunking if it exceeds Telegram's limit."""
    chunks = []
    while text:
        chunk = text[:MAX_MESSAGE_LENGTH]
        text = text[MAX_MESSAGE_LENGTH:]
        chunks.append(chunk)

    results = []
    for chunk in chunks:
        payload: dict = {
            "chat_id": chat_id,
            "text": chunk,
        }
        if parse_mode:
            payload["parse_mode"] = parse_mode

        data = json.dumps(payload).encode()
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                results.append(json.loads(resp.read().decode()))
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

    chat_id = os.environ.get("TELEGRAM_DEFAULT_CHAT_ID")
    parse_mode = None
    message_parts = []

    i = 0
    while i < len(args):
        if args[i] == "--chat-id" and i + 1 < len(args):
            chat_id = args[i + 1]
            i += 2
        elif args[i] == "--parse-mode" and i + 1 < len(args):
            parse_mode = args[i + 1]
            i += 2
        else:
            message_parts.append(args[i])
            i += 1

    message = " ".join(message_parts)

    if not message:
        print("Error: message is required", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not chat_id:
        print(
            "Error: chat_id is required (use --chat-id or set TELEGRAM_DEFAULT_CHAT_ID)",
            file=sys.stderr,
        )
        sys.exit(1)

    results = send_message(token, chat_id, message, parse_mode)

    if len(results) == 1:
        print(json.dumps(results[0], indent=2))
    else:
        print(json.dumps(results, indent=2))

    if any(not r.get("ok", True) for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
