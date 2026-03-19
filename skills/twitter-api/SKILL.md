---
name: twitter-api
description: "Read and write to the Twitter/X API — supports both write-only mode (free tier) and full read+write (paid tier). Post tweets, reply, like, retweet on free tier; additionally fetch timelines, search, and look up mentions on Basic tier ($200/mo) or higher. Handles OAuth 1.0a signing, bearer token auth, rate limits, and pagination. Use this skill whenever a task involves reading from or posting to Twitter/X, monitoring Twitter accounts, engaging with tweets, or analyzing Twitter activity — even if the user just says 'tweet' or 'post on X'."
metadata:
  strawpot:
    env:
      TWITTER_API_KEY:
        required: true
        description: Twitter/X API key (consumer key) from the developer portal
      TWITTER_API_SECRET:
        required: true
        description: Twitter/X API key secret (consumer secret)
      TWITTER_ACCESS_TOKEN:
        required: true
        description: OAuth 1.0a access token for the target account
      TWITTER_ACCESS_SECRET:
        required: true
        description: OAuth 1.0a access token secret
      TWITTER_BEARER_TOKEN:
        required: false
        description: Bearer token for app-only auth (read-only). Not needed on free tier — free tier uses OAuth for posting and has no read access. Required for read endpoints on Basic tier or higher.
---

# Twitter/X API

Interact with Twitter/X API v2 using the bundled helper script at `scripts/twitter_oauth.py`. The script handles OAuth 1.0a signing for write operations and bearer token auth for reads — you never need to construct auth headers manually.

## Access Tier

> **Current configuration: FREE TIER (post-only)**

The free tier supports **write operations only** plus basic identity lookup:

| Endpoint | Free Tier | Basic ($200/mo)+ |
|---|---|---|
| POST /2/tweets (post, reply) | ✅ 17 posts / 24hr | ✅ |
| POST likes, retweets | ✅ | ✅ |
| GET /2/users/me | ✅ 75 / 15min | ✅ |
| GET /2/users/:id/tweets (timeline) | ❌ 403 | ✅ |
| GET /2/tweets/search/recent | ❌ 403 | ✅ |
| GET /2/users/:id/mentions | ❌ 403 | ✅ |
| GET /2/users/by/username/:username | ❌ 403 | ✅ |

**On free tier, all read endpoints except `/2/users/me` will return HTTP 403.** Do not attempt them — they will fail. If you need read access, the account must be upgraded to Basic tier ($200/mo) or higher in the Twitter Developer Portal.

## Making requests

Use the helper script for all API calls. It reads credentials from environment variables automatically.

```bash
# GET request (uses bearer token if available, falls back to OAuth)
python scripts/twitter_oauth.py GET "<url>"

# POST request (always uses OAuth 1.0a)
python scripts/twitter_oauth.py POST "<url>" '<json-body>'
```

The script prints JSON to stdout and exits with code 1 on HTTP errors.

## Look up your own user ID

Most endpoints require a numeric user ID. Get it first:

```bash
python scripts/twitter_oauth.py GET "https://api.x.com/2/users/me?user.fields=id,username,public_metrics"
```

Save the `data.id` value — you'll need it for timeline, mentions, likes, and retweet endpoints.

## Operations

### Read timeline

> ⚠️ **Requires Basic tier or higher — not available on free tier** (returns 403)

```bash
python scripts/twitter_oauth.py GET \
  "https://api.x.com/2/users/{user_id}/tweets?max_results=10&tweet.fields=created_at,public_metrics,conversation_id"
```

### Search recent tweets

> ⚠️ **Requires Basic tier or higher — not available on free tier** (returns 403)

```bash
python scripts/twitter_oauth.py GET \
  "https://api.x.com/2/tweets/search/recent?query={query}&max_results=10&tweet.fields=created_at,public_metrics,author_id"
```

URL-encode the query parameter. Supports operators like `from:username`, `#hashtag`, `"exact phrase"`, `-exclude`.

### Get mentions

> ⚠️ **Requires Basic tier or higher — not available on free tier** (returns 403)

```bash
python scripts/twitter_oauth.py GET \
  "https://api.x.com/2/users/{user_id}/mentions?max_results=10&tweet.fields=created_at,public_metrics,conversation_id,in_reply_to_user_id"
```

### Post a tweet

```bash
python scripts/twitter_oauth.py POST \
  "https://api.x.com/2/tweets" \
  '{"text": "Your tweet text here"}'
```

Twitter/X enforces a 280-character limit on tweet text.

### Reply to a tweet

```bash
python scripts/twitter_oauth.py POST \
  "https://api.x.com/2/tweets" \
  '{"text": "Your reply", "reply": {"in_reply_to_tweet_id": "TWEET_ID"}}'
```

### Like a tweet

```bash
python scripts/twitter_oauth.py POST \
  "https://api.x.com/2/users/{user_id}/likes" \
  '{"tweet_id": "TWEET_ID"}'
```

### Retweet

```bash
python scripts/twitter_oauth.py POST \
  "https://api.x.com/2/users/{user_id}/retweets" \
  '{"tweet_id": "TWEET_ID"}'
```

### Look up a user by username

> ⚠️ **Requires Basic tier or higher — not available on free tier** (returns 403)

```bash
python scripts/twitter_oauth.py GET \
  "https://api.x.com/2/users/by/username/{username}?user.fields=public_metrics,description,created_at"
```

## Rate limits

Twitter API v2 enforces per-endpoint rate limits that vary by access tier (free, basic, pro).

### Free tier limits (current)

| Endpoint | Limit | Window | Notes |
|---|---|---|---|
| POST /2/tweets | 17 | 24 hours | Only write endpoint available |
| GET /2/users/me | 75 | 15 minutes | Only read endpoint available |

### Basic tier limits ($200/mo)

| Endpoint | Limit | Window |
|---|---|---|
| POST /2/tweets | 100 | 24 hours |
| GET /2/tweets/search/recent | 60 | 15 minutes |
| GET /2/users/:id/tweets | 100 | 24 hours |
| GET /2/users/:id/mentions | 100 | 24 hours |
| GET /2/users/me | 75 | 15 minutes |

> **Note:** On free tier, all read endpoints except `/2/users/me` return **HTTP 403** — do not attempt them.

If the script returns a response with `"status": 429`, stop immediately. Do not retry in a loop — check the `x-rate-limit-reset` header in the response (Unix timestamp) and report to the caller when they can resume. Budget your reads to stay well under limits, especially for the 24-hour windows.

## Pagination

List endpoints include `meta.next_token` when more results exist. Append it to the next request:

```bash
python scripts/twitter_oauth.py GET \
  "https://api.x.com/2/users/{user_id}/tweets?max_results=10&pagination_token={next_token}&tweet.fields=created_at,public_metrics"
```

Stop when `meta.next_token` is absent or you have sufficient data. Avoid paginating aggressively — each page counts toward rate limits.

## Error handling

The helper script returns the full error response as JSON on failure. Common errors:

| Status | Meaning | Action |
|---|---|---|
| 401 | Invalid or expired credentials | Check env vars are set correctly |
| 403 | Not authorized for this endpoint | On free tier, do not retry — read endpoints (except /2/users/me) require Basic tier ($200/mo). On paid tier, check app permissions in developer portal |
| 429 | Rate limited | Stop and wait until `x-rate-limit-reset` |
| 400 | Bad request (malformed JSON, invalid params) | Fix the request payload |
