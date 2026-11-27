def _key(key: str) -> str:
    cleaned = "".join(c for c in key.lower() if c.isalpha())
    if not cleaned:
        raise ValueError("مفتاح Vigenère يجب أن يحتوي على أحرف")
    return cleaned


def transform(text: str, key: str, decrypt: bool = False) -> str:
    key = _key(key)
    index, output = 0, []
    for char in text:
        if char.isalpha() and char.isascii():
            base = 65 if char.isupper() else 97
            shift = ord(key[index % len(key)]) - 97
            if decrypt:
                shift = -shift
            output.append(chr((ord(char) - base + shift) % 26 + base))
            index += 1
        else:
            output.append(char)
    return "".join(output)


def encrypt(text: str, key: str) -> str:
    return transform(text, key)


def decrypt(text: str, key: str) -> str:
    return transform(text, key, True)
