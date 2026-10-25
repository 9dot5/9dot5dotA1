"""Authentication: signed, short-lived tokens.

This is a development and test verifier. Production verification is delegated to Authentik (ADR-0012).
The Principal shape is kept so that the swap changes this module only.
Token format: base64url(JSON payload) "." base64url(HMAC-SHA256(key, payload)).
"""

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from .errors import Unauthenticated

KINDS = ("human", "agent", "workflow")
MIN_KEY_BYTES = 32


@dataclass(frozen=True)
class Principal:
    sub: str
    kind: str
    roles: tuple
    client_id: str


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def mint(key: bytes, sub: str, kind: str, roles: Iterable[str], client_id: str,
         ttl_s: int = 3600, now: Optional[float] = None) -> str:
    """Create a token. Used by the owner's issuing tool and by tests, never by an agent."""
    if kind not in KINDS:
        raise ValueError(f"unknown kind {kind!r}")
    issued = int(now if now is not None else time.time())
    payload = json.dumps(
        {"sub": sub, "kind": kind, "roles": sorted(roles), "client_id": client_id, "exp": issued + ttl_s},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    sig = hmac.new(key, payload, hashlib.sha256).digest()
    return _b64(payload) + "." + _b64(sig)


class TokenVerifier:
    def __init__(self, key: bytes, clock: Callable[[], float] = time.time):
        if len(key) < MIN_KEY_BYTES:
            raise ValueError(f"signing key must be at least {MIN_KEY_BYTES} bytes")
        self._key = key
        self._clock = clock

    def verify(self, token: Optional[str]) -> Principal:
        if not token or token.count(".") != 1:
            raise Unauthenticated("missing or malformed token")
        body, sig = token.split(".")
        try:
            payload = _unb64(body)
            given = _unb64(sig)
        except Exception as error:  # noqa: BLE001 - any decode failure is a refusal
            raise Unauthenticated("token is not valid base64") from error
        expected = hmac.new(self._key, payload, hashlib.sha256).digest()
        if not hmac.compare_digest(given, expected):
            raise Unauthenticated("bad token signature")
        try:
            data = json.loads(payload)
        except ValueError as error:
            raise Unauthenticated("token payload is not JSON") from error
        if data.get("kind") not in KINDS:
            raise Unauthenticated("unknown principal kind")
        if int(data.get("exp", 0)) <= int(self._clock()):
            raise Unauthenticated("token expired")
        return Principal(
            sub=str(data["sub"]),
            kind=data["kind"],
            roles=tuple(data.get("roles", [])),
            client_id=str(data.get("client_id", "")),
        )
