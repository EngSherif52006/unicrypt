import time
from . import aes, caesar, des, hill, playfair, rail_fence, vigenere

ALGORITHMS = {
    "caesar": {"label": "Caesar Cipher", "kind": "classical", "warning": "سهل الكسر؛ تعليمي فقط", "module": caesar},
    "hill": {"label": "Hill Cipher", "kind": "classical", "warning": "ضعيف أمام التحليل الحديث؛ تعليمي فقط", "module": hill},
    "vigenere": {"label": "Vigenère Cipher", "kind": "classical", "warning": "قابل للتحليل عند تكرار المفتاح", "module": vigenere},
    "playfair": {"label": "Playfair Cipher", "kind": "classical", "warning": "غير مناسب للسرية الحديثة", "module": playfair},
    "rail_fence": {"label": "Rail Fence Cipher", "kind": "classical", "warning": "تبديل نصي بلا أمان حقيقي", "module": rail_fence},
    "des": {"label": "DES", "kind": "modern-legacy", "warning": "متقادم ولا يصلح للبيانات السرية", "module": des},
    "aes": {"label": "AES-256-GCM", "kind": "modern", "warning": "مناسب للتجربة الآمنة عند إدارة المفتاح جيدًا", "module": aes},
}


def encrypt(algorithm: str, plaintext: str, key: str) -> dict:
    if algorithm not in ALGORITHMS:
        raise ValueError("خوارزمية غير مدعومة")
    started = time.perf_counter()
    if algorithm == "aes":
        result = aes.encrypt(plaintext, key)
    else:
        result = {"ciphertext": ALGORITHMS[algorithm]["module"].encrypt(plaintext, key), "nonce": "", "tag": "", "algorithm": algorithm.upper()}
    result.update({"encryption_ms": round((time.perf_counter() - started) * 1000, 4), "metadata": ALGORITHMS[algorithm] | {"module": None}})
    return result


def decrypt(algorithm: str, ciphertext: str, key: str, nonce: str | None = None, tag: str | None = None) -> dict:
    if algorithm not in ALGORITHMS:
        raise ValueError("خوارزمية غير مدعومة")
    started = time.perf_counter()
    if algorithm == "aes":
        if not nonce or not tag:
            raise ValueError("AES-GCM يحتاج nonce وauthentication tag")
        plaintext = aes.decrypt(ciphertext, key, nonce, tag)
    else:
        plaintext = ALGORITHMS[algorithm]["module"].decrypt(ciphertext, key)
    return {"plaintext": plaintext, "decryption_ms": round((time.perf_counter() - started) * 1000, 4)}
