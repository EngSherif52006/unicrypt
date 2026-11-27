import base64
import hashlib
from Crypto.Cipher import DES


def _key(key: str) -> bytes:
    return hashlib.sha256(key.encode()).digest()[:8]


def encrypt(text: str, key: str) -> str:
    cipher = DES.new(_key(key), DES.MODE_EAX)
    data = cipher.encrypt(text.encode())
    return base64.urlsafe_b64encode(cipher.nonce + cipher.digest() + data).decode()


def decrypt(ciphertext: str, key: str) -> str:
    raw = base64.urlsafe_b64decode(ciphertext.encode())
    # PyCryptodome يستخدم tag بطول كتلة DES (8 bytes) في EAX.
    nonce, tag, data = raw[:16], raw[16:24], raw[24:]
    cipher = DES.new(_key(key), DES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(data)
    cipher.verify(tag)
    return plaintext.decode()
