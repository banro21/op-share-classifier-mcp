import hashlib
import logging
from urllib.parse import urlparse

import httpx

from .derive import derive

logger = logging.getLogger(__name__)

SHARE_API = "https://share.1password.com/api/v1/share/{uuid}"


async def classify(url: str) -> dict:
    parsed = urlparse(url)
    fragment = parsed.fragment
    if not fragment:
        return {"access": "malformed"}

    try:
        uuid_b32, token_b32 = derive(fragment)
    except ValueError:
        return {"access": "malformed"}

    hash_prefix = hashlib.sha256(url.encode()).hexdigest()[:12]

    httpx_logger = logging.getLogger("httpx")
    prev_level = httpx_logger.level
    httpx_logger.setLevel(logging.WARNING)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                SHARE_API.format(uuid=uuid_b32),
                headers={
                    "OP-Share-Token": token_b32,
                    "OP-Language": "en",
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0",
                },
            )
    except httpx.TransportError:
        logger.warning("probe_error hash_prefix=%s", hash_prefix)
        return {"access": "probe_error"}
    finally:
        httpx_logger.setLevel(prev_level)

    if resp.status_code == 200:
        try:
            body = resp.json()
        except Exception:
            return {"access": f"http_{resp.status_code}"}
        result = {"access": "public"}
        if "templateUuid" in body:
            result["template"] = body["templateUuid"]
        if "expiresAt" in body:
            result["expires_at"] = body["expiresAt"]
        if "accountType" in body:
            result["account_type"] = body["accountType"]
        return result

    reason = None
    try:
        body = resp.json()
        reason = body.get("reason")
    except Exception:
        pass

    if resp.status_code == 401 and reason == "unauthorized":
        return {"access": "email_restricted"}

    reason_map = {
        "expired": "expired",
        "max_views": "max_views",
        "not_found": "not_found",
    }
    if reason in reason_map:
        return {"access": reason_map[reason]}

    return {"access": f"http_{resp.status_code}"}
