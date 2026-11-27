def _square(key: str):
    chars = []
    for char in (key.lower() + "abcdefghiklmnopqrstuvwxyz"):
        if char == "j":
            char = "i"
        if char.isalpha() and char not in chars:
            chars.append(char)
    return [chars[i:i + 5] for i in range(0, 25, 5)]


def _positions(square):
    return {square[r][c]: (r, c) for r in range(5) for c in range(5)}


def _pairs(text: str):
    text = "".join(c for c in text.lower() if c.isalpha()).replace("j", "i")
    out, i = [], 0
    while i < len(text):
        a = text[i]
        b = text[i + 1] if i + 1 < len(text) else "x"
        if a == b:
            out.append((a, "x")); i += 1
        else:
            out.append((a, b)); i += 2
    return out


def _transform(text: str, key: str, direction: int) -> str:
    square, pos, out = _square(key), None, []
    pos = _positions(square)
    for a, b in _pairs(text) if direction == 1 else [(text[i], text[i + 1]) for i in range(0, len(text), 2)]:
        ra, ca = pos[a]; rb, cb = pos[b]
        if ra == rb:
            out += [square[ra][(ca + direction) % 5], square[rb][(cb + direction) % 5]]
        elif ca == cb:
            out += [square[(ra + direction) % 5][ca], square[(rb + direction) % 5][cb]]
        else:
            out += [square[ra][cb], square[rb][ca]]
    return "".join(out)


def encrypt(text: str, key: str) -> str:
    return _transform(text, key, 1)


def decrypt(text: str, key: str) -> str:
    return _transform(text, key, -1)
