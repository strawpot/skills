---
name: content-calendar
description: "Manage a shared content calendar for coordinating posts across platforms (Twitter, Reddit, Moltbook, etc.). Track what has been posted, what is scheduled, and prevent cross-channel duplication. Use this skill whenever a task involves scheduling content, checking what has been posted recently, coordinating between marketing channels, or managing a content pipeline. Also trigger when the user asks what was recently posted, wants to log a published post, check for duplicate content across channels, or get a publishing summary — even if they don't say 'calendar' explicitly."
metadata:
  strawpot:
    tools:
      curl:
        description: HTTP client for GUI API calls
        install:
          macos: brew install curl
          linux: apt install curl
          windows: winget install cURL.cURL
      python3:
        description: Python 3 interpreter for JSON formatting
        install:
          macos: brew install python3
          linux: apt install python3
          windows: winget install Python.Python.3
---

# Content Calendar

A shared content calendar for coordinating posts across marketing channels. The calendar is managed through the StrawPot GUI API and serves as the single source of truth for all content activity across platforms.

## API Base

```
http://127.0.0.1:8741/api
```

Check if GUI is running:

```bash
curl -s http://127.0.0.1:8741/api/health
```

If not running, start it with `strawpot gui --port 8741`.

## List calendar entries

```bash
# All entries (default: last 30 days)
curl -s http://127.0.0.1:8741/api/content-calendar | python3 -m json.tool

# Filter by platform
curl -s "http://127.0.0.1:8741/api/content-calendar?platform=twitter" | python3 -m json.tool

# Filter by status
curl -s "http://127.0.0.1:8741/api/content-calendar?status=scheduled" | python3 -m json.tool

# Filter by date range
curl -s "http://127.0.0.1:8741/api/content-calendar?from=2025-01-01&to=2025-01-31" | python3 -m json.tool

# Combine filters
curl -s "http://127.0.0.1:8741/api/content-calendar?platform=moltbook&status=published&from=2025-01-01" | python3 -m json.tool
```

Platform values: `twitter`, `reddit`, `moltbook`, `linkedin`, `blog`.
Status values: `draft`, `scheduled`, `published`, `failed`.

## Create a calendar entry

```bash
curl -s -X POST http://127.0.0.1:8741/api/content-calendar \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "twitter",
    "title": "Brief description of the content",
    "body": "The actual post content or a summary for longer content",
    "status": "draft",
    "scheduled_at": "2025-02-01T14:00:00Z",
    "tags": ["product-launch", "announcement"],
    "campaign": "q1-launch"
  }'
```

## Update a calendar entry

```bash
curl -s -X PUT http://127.0.0.1:8741/api/content-calendar/{id} \
  -H "Content-Type: application/json" \
  -d '{
    "status": "published",
    "published_at": "2025-02-01T14:05:00Z",
    "external_id": "1234567890",
    "external_url": "https://x.com/account/status/1234567890"
  }'
```

After successfully posting content via a platform API, always update the calendar entry with:
- `status` set to `published`
- `published_at` with the actual publish timestamp
- `external_id` with the platform's post ID
- `external_url` with a link to the published content

If posting fails, update with `status` set to `failed` and add an `error` field with the reason.

## Delete a calendar entry

```bash
curl -s -X DELETE http://127.0.0.1:8741/api/content-calendar/{id}
```

Only delete draft entries. Published entries should be kept for historical tracking.

## Check for duplicates

Before creating content for any platform, check what has been recently published or scheduled to avoid cross-channel duplication:

```bash
# Check all platforms for recent posts in the same campaign
curl -s "http://127.0.0.1:8741/api/content-calendar?campaign=q1-launch&status=published" | python3 -m json.tool

# Check all platforms for posts with overlapping tags
# Note: date -v-7d is macOS/BSD syntax. On Linux, use: date -u -d '7 days ago' +%Y-%m-%d
# For portability: python3 -c "from datetime import datetime,timedelta; print((datetime.utcnow()-timedelta(days=7)).strftime('%Y-%m-%d'))"
curl -s "http://127.0.0.1:8741/api/content-calendar?tag=product-launch&from=$(date -u -v-7d +%Y-%m-%d)" | python3 -m json.tool
```

When adapting content from one platform to another, reference the original entry's ID in the new entry:

```bash
curl -s -X POST http://127.0.0.1:8741/api/content-calendar \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "moltbook",
    "title": "Adapted version of Twitter post",
    "body": "Platform-specific adaptation of the content...",
    "status": "draft",
    "adapted_from": "original-entry-id",
    "tags": ["product-launch"],
    "campaign": "q1-launch"
  }'
```

## Get calendar summary

```bash
# Summary of posts by platform and status for the current week
curl -s http://127.0.0.1:8741/api/content-calendar/summary | python3 -m json.tool

# Summary for a specific period
curl -s "http://127.0.0.1:8741/api/content-calendar/summary?from=2025-01-01&to=2025-01-31" | python3 -m json.tool
```

Returns counts grouped by platform and status, plus a list of upcoming scheduled posts.

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platform` | string | yes | Target platform (`twitter`, `reddit`, `moltbook`, `linkedin`, `blog`) |
| `title` | string | yes | Brief description of the content |
| `body` | string | no | Full content or summary |
| `status` | string | yes | Entry status (`draft`, `scheduled`, `published`, `failed`) |
| `scheduled_at` | ISO 8601 | no | When the content should be published |
| `published_at` | ISO 8601 | no | When the content was actually published |
| `tags` | array | no | Content tags for categorization and duplicate detection |
| `campaign` | string | no | Campaign identifier for grouping related content |
| `adapted_from` | string | no | ID of the original entry this was adapted from |
| `external_id` | string | no | Post ID on the target platform |
| `external_url` | string | no | URL to the published post |
| `error` | string | no | Error message if publishing failed |
| `author` | string | auto | Set automatically to the role that created the entry |

## Workflow for marketers

1. **Before creating content**: Query the calendar for recent posts with the same campaign or tags to avoid duplication
2. **Draft content**: Create a calendar entry with `status: draft`
3. **Get approval**: Present the draft for review
4. **Publish**: Post via the platform API, then update the calendar entry to `published` with the external ID and URL
5. **Track**: Use the summary endpoint to report on publishing activity

## Error handling

| Status | Meaning | Action |
|---|---|---|
| Connection refused | GUI is not running | Start it with `strawpot gui --port 8741` |
| 404 | Entry not found | Verify the calendar entry ID exists |
| 400 | Bad request (missing required fields, invalid values) | Check the request body against the Fields table |

## Cross-channel coordination

Each marketing role should:
- **Always log posts** to the content calendar after publishing
- **Always check the calendar** before creating new content to see what other channels have posted
- **Never duplicate content word-for-word** across platforms — adapt it for each platform's audience
- **Use consistent campaigns and tags** so entries can be correlated across platforms
