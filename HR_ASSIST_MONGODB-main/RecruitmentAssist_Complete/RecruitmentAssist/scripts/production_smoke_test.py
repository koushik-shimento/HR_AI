#!/usr/bin/env python3
"""Production smoke test for the React + Flask Vercel deployment.

Usage:
  python scripts/production_smoke_test.py https://your-production-domain.vercel.app

Optional authenticated check:
  SMOKE_USERNAME=admin SMOKE_PASSWORD=... python scripts/production_smoke_test.py https://...

The script intentionally uses only the Python standard library so it can run in
CI or a clean deployment environment without adding a test-only dependency.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


TIMEOUT = 20


def request(base: str, path: str, *, method: str = "GET", body: bytes | None = None, headers: dict[str, str] | None = None):
    url = urllib.parse.urljoin(base.rstrip("/") + "/", path.lstrip("/"))
    req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
            raw = response.read()
            return response.status, response.headers.get_content_type(), raw
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, exc.headers.get_content_type(), raw


def assert_react(base: str, path: str) -> None:
    status, content_type, body = request(base, path)
    assert status == 200, f"{path}: expected 200, got {status}"
    assert content_type == "text/html", f"{path}: expected text/html, got {content_type}"
    assert b"<html" in body.lower(), f"{path}: response is not the React HTML document"
    print(f"PASS frontend {path} -> {status} {content_type}")


def assert_json_401(base: str) -> None:
    status, content_type, body = request(base, "/api/dashboard")
    assert status == 401, f"/api/dashboard: expected 401, got {status}"
    assert content_type == "application/json", f"/api/dashboard: expected JSON, got {content_type}"
    payload = json.loads(body)
    assert payload.get("error") == "Unauthorized", f"unexpected 401 body: {payload!r}"
    print("PASS /api/dashboard unauthenticated -> 401 application/json")


def assert_authenticated_dashboard(base: str) -> None:
    username = os.environ.get("SMOKE_USERNAME")
    password = os.environ.get("SMOKE_PASSWORD")
    token = os.environ.get("SMOKE_SESSION_TOKEN")

    if token:
        status, content_type, body = request(
            base,
            "/api/dashboard",
            headers={"X-Session-Token": token},
        )
    elif username and password:
        login_body = json.dumps({"username": username, "password": password}).encode()
        login_status, login_type, login_raw = request(
            base,
            "/api/login",
            method="POST",
            body=login_body,
            headers={"Content-Type": "application/json"},
        )
        assert login_status == 200, f"/api/login: expected 200, got {login_status}"
        assert login_type == "application/json", f"/api/login: expected JSON, got {login_type}"
        login = json.loads(login_raw)
        token = login.get("token")
        assert token, f"/api/login did not return a token: {login!r}"
        status, content_type, body = request(
            base,
            "/api/dashboard",
            headers={"X-Session-Token": token},
        )
    else:
        print("SKIP authenticated dashboard check: set SMOKE_SESSION_TOKEN or SMOKE_USERNAME/SMOKE_PASSWORD")
        return

    assert status == 200, f"/api/dashboard authenticated: expected 200, got {status}"
    assert content_type == "application/json", f"/api/dashboard authenticated: expected JSON, got {content_type}"
    payload = json.loads(body)
    assert isinstance(payload, dict), f"unexpected dashboard payload: {payload!r}"
    assert "metrics" in payload, f"dashboard response does not look like the MongoDB-backed handler: {payload!r}"
    print("PASS /api/dashboard authenticated -> 200 application/json")


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/production_smoke_test.py https://your-production-domain")
        return 2

    base = sys.argv[1]
    try:
        assert_react(base, "/")
        assert_react(base, "/jobs/1")
        assert_json_401(base)
        assert_authenticated_dashboard(base)
    except (AssertionError, json.JSONDecodeError, urllib.error.URLError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 1

    print("Production smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
