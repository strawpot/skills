---
name: notify-discord
description: "Send messages to Discord channels via webhooks. Use when a task needs to post results, alerts, reports, or notifications to a Discord channel — even if the user just says 'notify discord' or 'post to discord'."
metadata:
  strawpot:
    env:
      DISCORD_WEBHOOK_URL:
        required: true
        description: Discord webhook URL (from channel settings > Integrations > Webhooks)
---

# Discord Notifications

Send messages to Discord channels using the bundled helper script at `scripts/send.py`. The script uses Discord webhooks — no bot token or gateway connection needed.

## Sending a message

```bash
# Send to the configured webhook channel
python scripts/send.py "Your message here"

# Override webhook URL
python scripts/send.py --webhook-url "https://discord.com/api/webhooks/..." "Your message here"

# Send with a custom username
python scripts/send.py --username "StrawPot Bot" "Your message here"
```

The script prints the API response as JSON and exits with code 1 on errors.

## Setting up a webhook

1. Open Discord channel settings
2. Go to **Integrations** > **Webhooks**
3. Click **New Webhook**, name it, and copy the URL
4. Set `DISCORD_WEBHOOK_URL` to the copied URL

The webhook URL looks like: `https://discord.com/api/webhooks/1234567890/abcdefgh...`

## Message limits

Discord enforces a **2000 character** limit per message. The helper script automatically chunks longer messages into multiple sends.

## Error handling

| Status | Meaning | Action |
|--------|---------|--------|
| 400 | Bad request (empty message, invalid format) | Check message content |
| 401 | Invalid webhook URL | Check DISCORD_WEBHOOK_URL |
| 404 | Webhook deleted or invalid | Recreate the webhook in Discord |
| 429 | Rate limited | Wait `retry_after` seconds (included in response) |

## Examples

### Post a daily summary

```bash
python scripts/send.py "📊 **Daily Report — $(date +%Y-%m-%d)**

• Sessions: 5 completed, 0 failed
• Top project: myapp (3 sessions)
• Total duration: 12m 30s"
```

### Alert on failure

```bash
python scripts/send.py "⚠️ **Build failed for myapp**

Exit code: 1
Error: Tests failed in \`auth_test.py\`"
```
