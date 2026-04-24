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
export MCP_AUTH_TOKEN=your-secret-token
python -m op_share_classifier
```

The server listens on `$PORT` (default 8000). Health check: `GET /healthz`.

## Deploy (Natoma)

```bash
docker build -t op-share-classifier-mcp .
docker run -e MCP_AUTH_TOKEN=your-secret-token -p 8000:8000 op-share-classifier-mcp
```

## SECURITY

> **WARNING**: The URL fragment contains a cryptographic secret. Handle with care.

- `MCP_AUTH_TOKEN` must be set to a strong random secret; all MCP endpoints require `Authorization: Bearer <token>`.
- The server **never logs** the URL, fragment, UUID, or token — only a 12-hex-char SHA-256 prefix of the URL.
- A `public` classification **consumes one view** on the target share link. Always dedup before calling.
- Run as non-root (uid 10001) in Docker.
- Secrets must never be committed to source control.