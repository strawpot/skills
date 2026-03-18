---
name: notify-telegram
description: "Send messages to Telegram chats via the Bot API. Use when a task needs to post results, alerts, reports, or notifications to a Telegram group or DM — even if the user just says 'notify telegram' or 'send to telegram'."
metadata:
  strawpot:
    env:
      TELEGRAM_BOT_TOKEN:
        required: true
        description: Telegram bot API token from @BotFather
      TELEGRAM_DEFAULT_CHAT_ID:
        required: false
        description: Default chat ID to send to (numeric, e.g., -100123456789 for groups, 123456789 for DMs)
---

# Telegram Notifications

Send messages to Telegram chats using the bundled helper script at `scripts/send.py`. The script handles authentication, message chunking (4096 char limit), and Markdown formatting.

## Sending a message

```bash
# Send to default chat (uses TELEGRAM_DEFAULT_CHAT_ID)
python scripts/send.py "Your message here"

# Send to a specific chat
python scripts/send.py --chat-id "-100123456789" "Your message here"

# Send with Markdown formatting
python scripts/send.py --parse-mode MarkdownV2 "**Bold** and _italic_"
```

The script prints the API response as JSON and exits with code 1 on errors.

## Chat ID formats

| Type | Format | Example |
|------|--------|---------|
| Private chat (DM) | Positive integer | `123456789` |
| Group | Negative integer | `-123456789` |
| Supergroup/channel | `-100` prefix | `-100123456789` |

To find a chat ID: add the bot to the group, send a message, then check `https://api.telegram.org/bot<TOKEN>/getUpdates` — the `chat.id` field has the value you need.

## Message limits

Telegram enforces a **4096 character** limit per message. The helper script automatically chunks longer messages into multiple sends. Each chunk is sent as a separate message.

## Error handling

| Status | Meaning | Action |
|--------|---------|--------|
| 400 | Bad request (invalid chat_id, empty message) | Check chat_id format and message content |
| 401 | Invalid bot token | Check TELEGRAM_BOT_TOKEN is correct |
| 403 | Bot blocked by user or not in group | Bot must be added to the group and not blocked |
| 429 | Rate limited | Wait and retry (script reports retry_after seconds) |

## Examples

### Post a daily summary

```bash
python scripts/send.py "Daily Report — $(date +%Y-%m-%d)

Sessions: 5 completed, 0 failed
Top project: myapp (3 sessions)
Total duration: 12m 30s"
```

### Alert on failure

```bash
python scripts/send.py --chat-id "-100123456789" "⚠️ Build failed for myapp

Exit code: 1
Error: Tests failed in auth_test.py"
```
