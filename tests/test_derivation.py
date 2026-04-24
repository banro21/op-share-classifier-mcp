import pytest

from op_share_classifier.derive import derive


def test_vector_a():
    fragment = "V7fYd2V312sGjCVatruCsh_6Dg0CZMA2V9Tk1RYXuzQ"
    uuid_b32, token_b32 = derive(fragment)
    assert uuid_b32 == "opfo7jcmid6c2r7mnyatwfmrte"
    assert token_b32 == "mgq6zq45lq5ofzdbooe3m734cm"


def test_vector_b():
    fragment = "8ENDE0hZAsEYYQyTPOj3NdU-SVVFR_wtHuBBSSNC31k"
    uuid_b32, token_b32 = derive(fragment)
    assert uuid_b32 == "c5phb4omvdjndrurpzf5xuqrqi"
    assert token_b32 == "xnqdlvsaopbc2ugrzyqgqu6gcu"


def test_malformed_fragment_raises():
    with pytest.raises(ValueError, match="malformed fragment"):
        derive("not-valid-base64!!!")


def test_short_fragment_raises():
    with pytest.raises(ValueError, match="malformed fragment"):
        # Only 8 bytes when decoded, not 32
        import base64

        short = base64.urlsafe_b64encode(b"tooshort").decode().rstrip("=")
        derive(short)
