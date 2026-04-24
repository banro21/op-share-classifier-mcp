import httpx
import pytest
import respx

from op_share_classifier.classify import classify

FRAGMENT = "V7fYd2V312sGjCVatruCsh_6Dg0CZMA2V9Tk1RYXuzQ"
URL = f"https://share.1password.com/s#{FRAGMENT}"
API_URL = "https://share.1password.com/api/v1/share/opfo7jcmid6c2r7mnyatwfmrte"


@respx.mock
@pytest.mark.asyncio
async def test_200_public():
    respx.get(API_URL).mock(
        return_value=httpx.Response(
            200,
            json={"templateUuid": "003", "expiresAt": "2026-05-01T00:00:00Z", "accountType": "B"},
        )
    )
    result = await classify(URL)
    assert result["access"] == "public"
    assert result["template"] == "003"
    assert result["expires_at"] == "2026-05-01T00:00:00Z"
    assert result["account_type"] == "B"


@respx.mock
@pytest.mark.asyncio
async def test_401_unauthorized():
    respx.get(API_URL).mock(return_value=httpx.Response(401, json={"reason": "unauthorized"}))
    result = await classify(URL)
    assert result["access"] == "email_restricted"


@respx.mock
@pytest.mark.asyncio
async def test_expired():
    respx.get(API_URL).mock(return_value=httpx.Response(410, json={"reason": "expired"}))
    result = await classify(URL)
    assert result["access"] == "expired"


@respx.mock
@pytest.mark.asyncio
async def test_max_views():
    respx.get(API_URL).mock(return_value=httpx.Response(410, json={"reason": "max_views"}))
    result = await classify(URL)
    assert result["access"] == "max_views"


@respx.mock
@pytest.mark.asyncio
async def test_not_found():
    respx.get(API_URL).mock(return_value=httpx.Response(404, json={"reason": "not_found"}))
    result = await classify(URL)
    assert result["access"] == "not_found"


@respx.mock
@pytest.mark.asyncio
async def test_500():
    respx.get(API_URL).mock(return_value=httpx.Response(500, json={}))
    result = await classify(URL)
    assert result["access"] == "http_500"


@respx.mock
@pytest.mark.asyncio
async def test_network_timeout():
    respx.get(API_URL).mock(side_effect=httpx.ConnectTimeout("timeout"))
    result = await classify(URL)
    assert result["access"] == "probe_error"


@pytest.mark.asyncio
async def test_malformed_fragment_too_short():
    result = await classify("https://share.1password.com/s#tooshort")
    assert result["access"] == "malformed"


@pytest.mark.asyncio
async def test_malformed_base64url():
    result = await classify("https://share.1password.com/s#!!!invalid!!!")
    assert result["access"] == "malformed"
