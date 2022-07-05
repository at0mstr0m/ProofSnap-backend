from typing import Tuple

from ecdsa import VerifyingKey, SigningKey, NIST521p
from ecdsa.keys import BadSignatureError

# the currently used curve
CURVE = NIST521p


def generate_key_pair() -> Tuple[str, str]:
    private_key = SigningKey.generate(curve=CURVE)
    public_key = private_key.verifying_key
    # to_string() returns type byte, but hex() returns type str
    return private_key.to_string().hex(), public_key.to_string().hex()


def get_public_key_from_string(public_key: str) -> VerifyingKey:
    return VerifyingKey.from_string(bytes.fromhex(public_key), curve=CURVE)


def get_private_key_from_string(private_key: str) -> SigningKey:
    return SigningKey.from_string(bytes.fromhex(private_key), curve=CURVE)


def generate_signature(data: str, private_key: str) -> str:
    return get_private_key_from_string(private_key).sign(data.encode()).hex()


def verify_signature(data: str, public_key: str, signature: str) -> bool:
    try:
        return get_public_key_from_string(public_key).verify(bytes.fromhex(signature), data.encode())
    except BadSignatureError:
        return False
