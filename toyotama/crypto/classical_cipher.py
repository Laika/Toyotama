def rot(plaintext: str | bytes, rotate: int = 13) -> bytes:
    """ROTxx

    Rotate a string.

    Args:
        plaintext (str or bytes): The plaintext.
        rotate (int, optional): The number to rotate. Defaults to 13
    Returns:
        str or bytes: The rotated text.
    """
    rotate %= 26
    if isinstance(plaintext, str):
        plaintext = plaintext.encode()
    r = []
    for c in plaintext:
        if ord("A") <= c <= ord("Z"):
            r.append((c - ord("A") + rotate) % 26 + ord("A"))
        elif ord("a") <= c <= ord("z"):
            r.append((c - ord("a") + rotate) % 26 + ord("a"))
        else:
            r.append(c)

    return bytes(r)
