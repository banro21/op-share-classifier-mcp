import httpx
import pytest
import respx

from op_share_classifier.classify import classify


@respx.mock
@pytest.mark.asyncio
async def test_classify_tool_email_restricted():
    respx.get("https://share.1password.com/api/v1/share/opfo7jcmid6c2r7mnyatwfmrte").mock(
        return_value=httpx.Response(401, json={"reason": "unauthorized"})
    )
    result = await classify(
        "https://share.1password.com/s#V7fYd2V312sGjCVatruCsh_6Dg0CZMA2V9Tk1RYXuzQ"
    )
    assert result["access"] == "email_restricted"


@respx.mock
@pytest.mark.asyncio
async def test_classify_tool_public():
    respx.get("https://share.1password.com/api/v1/share/opfo7jcmid6c2r7mnyatwfmrte").mock(
        return_value=httpx.Response(
            200,
            json={"templateUuid": "003", "expiresAt": "2026-05-01T00:00:00Z", "accountType": "B"},
        )
    )
    result = await classify(
        "https://share.1password.com/s#V7fYd2V312sGjCVatruCsh_6Dg0CZMA2V9Tk1RYXuzQ"
    )
    assert result["access"] == "public"
    assert result["template"] == "003"


def test_create_app_returns_asgi_app():
    from op_share_classifier.server import create_app

    app = create_app()
    assert app is not None
    # FastMCP's streamable_http_app returns a Starlette instance
    assert hasattr(app, "router")
