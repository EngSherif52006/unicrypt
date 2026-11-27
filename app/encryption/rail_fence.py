def encrypt(text: str, key: str) -> str:
    rails = int(key)
    if rails < 2:
        return text
    rows = [[] for _ in range(rails)]
    row, direction = 0, 1
    for char in text:
        rows[row].append(char)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction
    return "".join("".join(r) for r in rows)


def decrypt(ciphertext: str, key: str) -> str:
    rails = int(key)
    if rails < 2:
        return ciphertext
    pattern, row, direction = [], 0, 1
    for _ in ciphertext:
        pattern.append(row)
        if row == 0:
            direction = 1
        elif row == rails - 1:
            direction = -1
        row += direction
    counts = [pattern.count(i) for i in range(rails)]
    rows, index = [], 0
    for count in counts:
        rows.append(list(ciphertext[index:index + count]))
        index += count
    return "".join(rows[r].pop(0) for r in pattern)
