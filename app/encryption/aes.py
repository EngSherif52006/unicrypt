import base64
import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def derive_key(key: str) -> bytes:
    return hashlib.sha256(key.encode("utf-8")).digest()


def encrypt(text: str, key: str) -> dict[str, str]:
    nonce = secrets.token_bytes(12)
    combined = AESGCM(derive_key(key)).encrypt(nonce, text.encode("utf-8"), None)
    ciphertext, tag = combined[:-16], combined[-16:]
    encoder = base64.urlsafe_b64encode
    return {"ciphertext": encoder(ciphertext).decode(), "nonce": encoder(nonce).decode(), "tag": encoder(tag).decode(), "algorithm": "AES-256-GCM"}


def decrypt(ciphertext: str, key: str, nonce: str, tag: str) -> str:
    decoder = base64.urlsafe_b64decode
    combined = decoder(ciphertext) + decoder(tag)
    plaintext = AESGCM(derive_key(key)).decrypt(decoder(nonce), combined, None)
    return plaintext.decode("utf-8")
