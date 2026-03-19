#!/usr/bin/env python3
"""
Twitter/X API helper with OAuth 1.0a signing.

Usage:
  # GET (bearer token auth)
  python twitter_oauth.py GET "https://api.x.com/2/users/me"

  # POST (OAuth 1.0a signed)
  python twitter_oauth.py POST "https://api.x.com/2/tweets" '{"text": "Hello world"}'

Environment variables required:
  TWITTER_API_KEY, TWITTER_API_SECRET,
  TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

For read-only GET requests, TWITTER_BEARER_TOKEN is used if set.
For POST/PUT/DELETE, OAuth 1.0a signing is always used.

Output: JSON response body to stdout. Exit code 1 on error.
"""

import hashlib
import hmac
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid
from typing import Optional


def _percent_encode(s: str) -> str:
    return urllib.parse.quote(str(s), safe="")


def _build_oauth_signature(
    method: str,
    url: str,
    params: dict,
    consumer_secret: str,
    token_secret: str,
) -> str:
    sorted_params = "&".join(
        f"{_percent_encode(k)}={_percent_encode(v)}"
        for k, v in sorted(params.items())
    )
    base_string = "&".join([
        method.upper(),
        _percent_encode(url),
        _percent_encode(sorted_params),
    ])
    signing_key = f"{_percent_encode(consumer_secret)}&{_percent_encode(token_secret)}"
    digest = hmac.new(
        signing_key.encode(), base_string.encode(), hashlib.sha1
    ).digest()
    import base64
    return base64.b64encode(digest).decode()


def _build_oauth_header(method: str, url: str) -> str:
    api_key = os.environ["TWITTER_API_KEY"]
    api_secret = os.environ["TWITTER_API_SECRET"]
    access_token = os.environ["TWITTER_ACCESS_TOKEN"]
    access_secret = os.environ["TWITTER_ACCESS_SECRET"]

    oauth_params = {
        "oauth_consumer_key": api_key,
        "oauth_nonce": uuid.uuid4().hex,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    # Parse query params from URL for signature base
    parsed = urllib.parse.urlparse(url)
    query_params = dict(urllib.parse.parse_qsl(parsed.query))
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    all_params = {**oauth_params, **query_params}
    signature = _build_oauth_signature(
        method, base_url, all_params, api_secret, access_secret
    )
    oauth_params["oauth_signature"] = signature

    header_parts = ", ".join(
        f'{_percent_encode(k)}="{_percent_encode(v)}"'
        for k, v in sorted(oauth_params.items())
    )
    return f"OAuth {header_parts}"


def request(method: str, url: str, body: Optional[str] = None) -> dict:
    method = method.upper()
    headers = {}

    if method == "GET" and os.environ.get("TWITTER_BEARER_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['TWITTER_BEARER_TOKEN']}"
    else:
        headers["Authorization"] = _build_oauth_header(method, url)

    if body is not None:
        headers["Content-Type"] = "application/json"
        data = body.encode()
    else:
        data = None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        try:
            error_json = json.loads(error_body)
        except json.JSONDecodeError:
            error_json = {"error": error_body}
        return {"status": e.code, "headers": dict(e.headers), **error_json}


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    method = sys.argv[1]
    url = sys.argv[2]
    body = sys.argv[3] if len(sys.argv) > 3 else None

    result = request(method, url, body)
    print(json.dumps(result, indent=2))

    if "status" in result and result["status"] >= 400:
        sys.exit(1)


if __name__ == "__main__":
    main()
