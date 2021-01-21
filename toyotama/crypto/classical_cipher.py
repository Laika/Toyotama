from functools import singledispatch


@singledispatch
def rot(s, rotate=13):
    rotate %= 26
    r = ""
    for c in s:
        if "A" <= c <= "Z":
            r += chr((ord(c) - ord("A") + rotate) % 26 + ord("A"))
        elif "a" <= c <= "z":
            r += chr((ord(c) - ord("a") + rotate) % 26 + ord("a"))
        else:
            r += c
    return r


@rot.register(str)
def rot_str(s, rotate=13):
    rotate %= 26
    r = ""
    for c in s:
        if "A" <= c <= "Z":
            r += chr((ord(c) - 65 + rotate) % 26 + 65)
        elif "a" <= c <= "z":
            r += chr((ord(c) - 97 + rotate) % 26 + 97)
        else:
            r += c
    return r


@rot.register(bytes)
def rot_bytes(s, rotate=13):
    rotate %= 26
    r = []
    for c in s:
        if "A" <= chr(c) <= "Z":
            r.append((c - 65 + rotate) % 26 + 65)
        elif "a" <= chr(c) <= "z":
            r.append((c - 97 + rotate) % 26 + 97)
        else:
            r.append(c)
    return bytes(r)


@singledispatch
def xor_string(s, t):
    raise TypeError("Both s and t must be str or bytes.")


@xor_string.register(str)
def xor_string_str(s, t):
    return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(s, t))


@xor_string.register(bytes)
def xor_string_bytes(s, t):
    return bytes([a ^ b for a, b in zip(s, t)])


def vigenere(cipher, key):
    pts = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    key = key.lower()
    key = [ord("a") - ord(c) for c in key]
    ans = ""
    i = 0
    for c in cipher:
        if c not in pts:
            ans += c
        else:
            ans += rot(c, key[i % len(key)])
            i += 1
    return "".join(ans)
