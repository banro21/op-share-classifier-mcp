import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("OP_LIVE_TEST"),
    reason="Set OP_LIVE_TEST=1 to run live tests",
)


@pytest.mark.asyncio
async def test_live_email_restricted():
    url = os.environ.get("OP_LIVE_EMAIL_RESTRICTED_URL")
    if not url:
        pytest.skip("OP_LIVE_EMAIL_RESTRICTED_URL not set")
    from op_share_classifier.classify import classify

    result = await classify(url)
    assert result["access"] == "email_restricted"


@pytest.mark.asyncio
async def test_live_public():
    url = os.environ.get("OP_LIVE_PUBLIC_URL")
    if not url:
        pytest.skip("OP_LIVE_PUBLIC_URL not set")
    from op_share_classifier.classify import classify

    result = await classify(url)
    assert result["access"] in {"public", "max_views"}
    if result["access"] == "public":
        assert result.get("template") == "003"
        assert result.get("account_type") == "B"
        assert result.get("expires_at", "").startswith("2026-05-")
