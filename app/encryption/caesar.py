def transform(text: str, shift: int, decrypt: bool = False) -> str:
    if decrypt:
        shift = -shift
    out = []
    for char in text:
        if "a" <= char <= "z":
            out.append(chr((ord(char) - 97 + shift) % 26 + 97))
        elif "A" <= char <= "Z":
            out.append(chr((ord(char) - 65 + shift) % 26 + 65))
        else:
            out.append(char)
    return "".join(out)


def encrypt(text: str, key: str) -> str:
    return transform(text, int(key), False)


def decrypt(text: str, key: str) -> str:
    return transform(text, int(key), True)
