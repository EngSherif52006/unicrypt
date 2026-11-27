import math


def _matrix(key: str):
    nums = [int(x.strip()) % 26 for x in key.split(",")]
    if len(nums) != 4:
        raise ValueError("مفتاح Hill يجب أن يكون أربعة أرقام مثل 3,3,2,5")
    a, b, c, d = nums
    det = (a * d - b * c) % 26
    if math.gcd(det, 26) != 1:
        raise ValueError("مصفوفة Hill غير قابلة للعكس modulo 26")
    return a, b, c, d


def _clean(text: str) -> str:
    return "".join(c.lower() for c in text if c.isalpha() and c.isascii())


def encrypt(text: str, key: str) -> str:
    a, b, c, d = _matrix(key)
    clean = _clean(text)
    if len(clean) % 2:
        clean += "x"
    out = []
    for i in range(0, len(clean), 2):
        x, y = ord(clean[i]) - 97, ord(clean[i + 1]) - 97
        out.extend([(a * x + b * y) % 26, (c * x + d * y) % 26])
    return "".join(chr(v + 97) for v in out)


def decrypt(text: str, key: str) -> str:
    a, b, c, d = _matrix(key)
    det = pow((a * d - b * c) % 26, -1, 26)
    ia, ib, ic, id_ = d * det % 26, -b * det % 26, -c * det % 26, a * det % 26
    clean = _clean(text)
    out = []
    for i in range(0, len(clean), 2):
        x, y = ord(clean[i]) - 97, ord(clean[i + 1]) - 97
        out.extend([(ia * x + ib * y) % 26, (ic * x + id_ * y) % 26])
    return "".join(chr(v + 97) for v in out).rstrip("x")
