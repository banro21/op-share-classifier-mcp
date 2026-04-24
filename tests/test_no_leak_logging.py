import logging

import httpx
import pytest
import respx

from op_share_classifier.classify import classify

FRAGMENT = "V7fYd2V312sGjCVatruCsh_6Dg0CZMA2V9Tk1RYXuzQ"
URL = f"https://share.1password.com/s#{FRAGMENT}"
API_URL = "https://share.1password.com/api/v1/share/opfo7jcmid6c2r7mnyatwfmrte"

SENSITIVE = [
    URL,
    FRAGMENT,
    "opfo7jcmid6c2r7mnyatwfmrte",
    "mgq6zq45lq5ofzdbooe3m734cm",
]


@respx.mock
@pytest.mark.asyncio
async def test_no_sensitive_data_in_logs(caplog):
    respx.get(API_URL).mock(return_value=httpx.Response(401, json={"reason": "unauthorized"}))
    with caplog.at_level(logging.DEBUG):
        result = await classify(URL)

    assert result["access"] == "email_restricted"

    for record in caplog.records:
        msg = record.getMessage()
        for sensitive in SENSITIVE:
            assert sensitive not in msg, (
                f"Sensitive string '{sensitive}' found in log record: {msg!r}"
            )
        # Also check raw args
        if record.args:
            args_str = str(record.args)
            for sensitive in SENSITIVE:
                assert sensitive not in args_str, (
                    f"Sensitive string '{sensitive}' found in log args: {args_str!r}"
                )
