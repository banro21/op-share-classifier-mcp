import base64

from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def _hkdf(ikm: bytes, info: bytes, length: int) -> bytes:
    h = HKDF(algorithm=SHA256(), length=length, salt=b"", info=info)
    return h.derive(ikm)


def derive(fragment: str) -> tuple[str, str]:
    padded = fragment + "=" * (-len(fragment) % 4)
    try:
        secret = base64.urlsafe_b64decode(padded)
    except Exception:
        raise ValueError("malformed fragment")
    if len(secret) != 32:
        raise ValueError("malformed fragment")

    uuid_bytes = _hkdf(secret, b"share_item_uuid", 16)
    token_bytes = _hkdf(secret, b"share_item_token", 16)
    _key_bytes = _hkdf(secret, b"share_item_encryption_key", 32)  # derived but unused

    def _b32(b: bytes) -> str:
        return base64.b32encode(b).decode("ascii").lower().rstrip("=")

    return _b32(uuid_bytes), _b32(token_bytes)
