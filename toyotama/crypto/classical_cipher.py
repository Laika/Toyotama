import typing

from functools import singledispatch


def rot(plaintext: typing.Union[str, bytes], rotate: int = 13):
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
        r = ""
        for c in plaintext:
            if "A" <= c <= "Z":
                r += chr((ord(c) - ord("A") + rotate) % 26 + ord("A"))
            elif "a" <= c <= "z":
                r += chr((ord(c) - ord("a") + rotate) % 26 + ord("a"))
            else:
                r += c
    else:
        r = b""
        for c in plaintext:
            if ord("A") <= c <= ord("Z"):
                r += chr((c - ord("A") + rotate) % 26 + ord("A"))
            elif "a" <= c <= "z":
                r += chr((c - ord("a") + rotate) % 26 + ord("a"))
            else:
                r += c

    return r


def XOR(A: typing.Union[str, bytes], B: typing.Union[str, bytes]):
    """XOR strings

    Calculate `A XOR B`.

    Args:
        A (str or bytes): The first string.
        B (str or bytes): The second string.
    Returns:
        str or bytes: The result of `A XOR B`.
    """


    if isinstance(A, str) and isinstance(B, bytes) or isinstance(A, bytes) and isinstance(B, str):
        raise TypeError("The type of A and B is not match.")
    if isinstance(A, str):
        return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(A, B))

    return bytes(a ^ b for a, b in zip(A, B))