---
name: reddit-api
description: "Read and write to the Reddit API — browse subreddits, submit posts, comment, reply, vote, search, and look up users. Handles OAuth2 authentication, rate limits, and pagination. Use this skill whenever a task involves reading from or posting to Reddit, monitoring subreddits, engaging in discussions, or analyzing Reddit activity — even if the user just says 'post on Reddit' or 'check Reddit'."
metadata:
  strawpot:
    env:
      REDDIT_CLIENT_ID:
        required: true
        description: Reddit OAuth2 app client ID from https://www.reddit.com/prefs/apps
      REDDIT_CLIENT_SECRET:
        required: true
        description: Reddit OAuth2 app client secret
      REDDIT_USERNAME:
        required: true
        description: Reddit account username for authentication
      REDDIT_PASSWORD:
        required: true
        description: Reddit account password for script-type OAuth2 apps
      REDDIT_USER_AGENT:
        required: false
        description: Custom User-Agent string. Defaults to "strawpot:reddit-api:v1.0 (by /u/{REDDIT_USERNAME})"
---

# Reddit API

Interact with Reddit's API using OAuth2 authentication. All requests go through `https://oauth.reddit.com` after obtaining an access token.

## Authentication

Reddit uses OAuth2 with the "script" app type for server-side automation. Obtain an access token before making API calls:

```bash
# Get OAuth2 access token
ACCESS_TOKEN=$(curl -s -X POST https://www.reddit.com/api/v1/access_token \
  -u "${REDDIT_CLIENT_ID}:${REDDIT_CLIENT_SECRET}" \
  -d "grant_type=password&username=${REDDIT_USERNAME}&password=${REDDIT_PASSWORD}" \
  -A "${REDDIT_USER_AGENT:-strawpot:reddit-api:v1.0}" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
```

Use this token in all subsequent requests:

```bash
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT:-strawpot:reddit-api:v1.0}" \
  "https://oauth.reddit.com/..."
```

Tokens expire after 1 hour. Re-authenticate if you receive a 401 response.

## Operations

### Read a subreddit

```bash
# Hot posts (default sort)
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/r/{subreddit}/hot?limit=10"

# Other sort options: new, top, rising, controversial
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/r/{subreddit}/top?t=week&limit=10"
```

The `t` parameter for `/top` and `/controversial` accepts: `hour`, `day`, `week`, `month`, `year`, `all`.

### Search posts

```bash
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/r/{subreddit}/search?q={query}&restrict_sr=true&sort=relevance&limit=10"

# Search across all of Reddit
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/search?q={query}&sort=relevance&limit=10"
```

URL-encode the query. Supports Reddit search syntax: `title:keyword`, `author:username`, `selftext:keyword`, `flair:name`.

### Get post comments

```bash
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/r/{subreddit}/comments/{post_id}?sort=best&limit=25"
```

Sort options: `best`, `top`, `new`, `controversial`, `old`, `qa`.

### Submit a text post

```bash
curl -s -X POST -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/api/submit" \
  -d "sr={subreddit}&kind=self&title={title}&text={body}&api_type=json"
```

### Submit a link post

```bash
curl -s -X POST -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/api/submit" \
  -d "sr={subreddit}&kind=link&title={title}&url={url}&api_type=json"
```

### Comment on a post or reply to a comment

```bash
curl -s -X POST -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/api/comment" \
  -d "thing_id={fullname}&text={comment_body}&api_type=json"
```

The `thing_id` is the fullname of the post (`t3_xxxxx`) or comment (`t1_xxxxx`).

### Vote on a post or comment

```bash
# Upvote (dir=1), downvote (dir=-1), unvote (dir=0)
curl -s -X POST -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/api/vote" \
  -d "id={fullname}&dir=1"
```

### Get user info

```bash
# Your own account
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/api/v1/me"

# Another user's profile
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/user/{username}/about"
```

### Get inbox / mentions

```bash
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/message/inbox?limit=25"

# Username mentions only
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/message/mentions?limit=25"
```

## Rate limits

Reddit enforces rate limits via response headers:

| Header | Description |
|---|---|
| `x-ratelimit-remaining` | Requests remaining in current window |
| `x-ratelimit-reset` | Seconds until the window resets |
| `x-ratelimit-used` | Requests used in current window |

General limits:
- **OAuth clients**: 60 requests per minute (1 per second sustained)
- **Posting**: Reddit enforces per-subreddit cooldowns for new accounts or low-karma users. If you receive a "RATELIMIT" error, the response includes a `ratelimit` field with the wait time in seconds.

If you receive a 429 response, stop immediately. Check `x-ratelimit-reset` and report to the caller when they can resume. Do not retry in a loop.

## Pagination

Reddit uses cursor-based pagination with `after` and `before` parameters:

```bash
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/r/{subreddit}/new?limit=25&after={after_fullname}"
```

The `after` value is the fullname of the last item in the previous response (found in `data.after`). Stop when `data.after` is `null` or you have sufficient data.

## Reddit fullname prefixes

| Prefix | Type |
|---|---|
| `t1_` | Comment |
| `t2_` | Account |
| `t3_` | Post (link) |
| `t4_` | Message |
| `t5_` | Subreddit |

## Error handling

| Status | Meaning | Action |
|---|---|---|
| 401 | Token expired or invalid | Re-authenticate to get a new access token |
| 403 | Forbidden (banned, private subreddit, insufficient permissions) | Check account standing and subreddit rules |
| 429 | Rate limited | Stop and wait until `x-ratelimit-reset` seconds |
| 400 | Bad request | Check request parameters and formatting |
| 503 | Reddit is temporarily unavailable | Wait a few seconds and retry once |

## Subreddit rules

Before posting to any subreddit, check its rules:

```bash
curl -s -H "Authorization: bearer ${ACCESS_TOKEN}" \
  -A "${REDDIT_USER_AGENT}" \
  "https://oauth.reddit.com/r/{subreddit}/about/rules"
```

Many subreddits have strict posting guidelines, flair requirements, and minimum account age or karma thresholds. Violating rules will get posts removed or the account banned.
