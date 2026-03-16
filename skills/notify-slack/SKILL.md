---
name: notify-slack
description: "Send messages to Slack channels and threads via the Web API. Use when a task needs to post results, alerts, reports, or notifications to a Slack channel — even if the user just says 'notify slack' or 'post to slack'."
metadata:
  strawpot:
    env:
      SLACK_BOT_TOKEN:
        required: true
        description: Slack bot token (xoxb-...) from your Slack app
      SLACK_DEFAULT_CHANNEL:
        required: false
        description: Default channel ID to post to (e.g., C0123456789)
---

# Slack Notifications

Send messages to Slack channels using the bundled helper script at `scripts/send.py`. The script handles authentication, message formatting, and thread replies.

## Sending a message

```bash
# Send to default channel (uses SLACK_DEFAULT_CHANNEL)
python scripts/send.py "Your message here"

# Send to a specific channel
python scripts/send.py --channel "C0123456789" "Your message here"

# Reply in a thread
python scripts/send.py --channel "C0123456789" --thread-ts "1234567890.123456" "Thread reply"
```

The script prints the API response as JSON and exits with code 1 on errors.

## Channel ID format

Slack uses channel IDs (not names) for the API. To find a channel ID:
1. Right-click the channel name in Slack
2. Click "View channel details"
3. The ID is at the bottom (starts with `C` for channels, `D` for DMs, `G` for group DMs)

| Type | Prefix | Example |
|------|--------|---------|
| Public channel | `C` | `C0123456789` |
| Private channel | `C` | `C9876543210` |
| DM | `D` | `D0123456789` |
| Group DM | `G` | `G0123456789` |

## Message limits

Slack allows up to **40,000 characters** per message in blocks. The helper script sends plain text messages via `chat.postMessage`. For very long messages, it chunks at 3900 characters to stay within safe limits.

## Error handling

| Error | Meaning | Action |
|-------|---------|--------|
| `not_authed` | Invalid or missing token | Check SLACK_BOT_TOKEN |
| `channel_not_found` | Invalid channel ID | Check channel ID format |
| `not_in_channel` | Bot not in channel | Invite the bot to the channel first |
| `too_many_attachments` | Message too complex | Simplify the message |
| `ratelimited` | Rate limited | Wait `Retry-After` seconds |

## Examples

### Post a daily summary

```bash
python scripts/send.py "📊 *Daily Report — $(date +%Y-%m-%d)*

• Sessions: 5 completed, 0 failed
• Top project: myapp (3 sessions)
• Total duration: 12m 30s"
```

### Alert on failure

```bash
python scripts/send.py --channel "C0123456789" "⚠️ *Build failed for myapp*

Exit code: 1
Error: Tests failed in \`auth_test.py\`"
```
