# op-share-classifier-mcp

An MCP server that classifies 1Password share links without opening them in a browser.

## Protocol Summary

The server derives a UUID and retrieval token from the URL fragment using HKDF-SHA256, then probes
the 1Password share API. It returns one of: `public`, `email_restricted`, `expired`, `max_views`,
`not_found`, `probe_error`, `malformed`, or `http_<N>`. A `public` result **consumes one view** on
the share link — callers must dedup by URL hash before invoking.

## Local Dev

```bash
pip install uv
uv pip install --system -e ".[dev]"
pytest tests/test_derivation.py tests/test_classify_mocked.py tests/test_no_leak_logging.py tests/test_server.py -v
ruff check src tests
ruff format src tests
```

## Running the Server

```bash
python -m op_share_classifier
```

The server listens on `$PORT` (default 8080). Health check: `GET /healthz`. MCP endpoint: `POST /mcp`.

## Deploy (Natoma)

```bash
docker build -t op-share-classifier-mcp .
docker run -p 8080:8080 op-share-classifier-mcp
```

> **Auth:** Natoma authenticates callers at its gateway; the MCP server does not enforce its own auth for repo-based custom apps. Do not set `MCP_AUTH_TOKEN`.

## SECURITY

> **WARNING**: The URL fragment contains a cryptographic secret. Handle with care.

- The server **never logs** the URL, fragment, UUID, or token — only a 12-hex-char SHA-256 prefix of the URL.
- A `public` classification **consumes one view** on the target share link. Always dedup before calling.
- Run as non-root (uid 10001) in Docker.
- Secrets must never be committed to source control.
- When deployed behind Natoma, caller authentication is enforced at the Natoma gateway; the server is only reachable via Natoma's internal network.
