from functools import singledispatch

from PIL import Image, ImageDraw

from .log import get_logger

logger = get_logger()


def urlencode(s, encoding="shift-jis", safe=":/&?="):
    from urllib.parse import quote_plus

    return quote_plus(s, encoding=encoding, safe=safe)


def urldecode(s, encoding="shift-jis"):
    from urllib.parse import unquote_plus

    return unquote_plus(s, encoding=encoding)


def to_block(x, block_size: int = 16):
    return [x[i : i + block_size] for i in range(0, len(x), block_size)]


@singledispatch
def b64_padding(s):
    raise TypeError("s must be str or bytes.")


@b64_padding.register(str)
def b64_padding_str(s):
    s += "=" * (-len(s) % 4)
    return s


@b64_padding.register(bytes)
def b64_padding_bytes(s):
    s += b"=" * (-len(s) % 4)
    return s


def binary_to_image(data, padding=5, size=5, rev=False, image_size=(1000, 1000)):
    bk, wh = (0, 0, 0), (255, 255, 255)
    image = Image.new("RGB", image_size, wh)
    rect = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(rect)
    draw.rectangle((0, 0, size, size), fill=bk)

    h, w = 0, 0
    x, y = 0, 0
    for pixel in data:
        if pixel == "\n":
            y += 1
            h += 1
            w = max(w, x)
            x = 0
        else:
            if (pixel == "1") ^ rev:
                image.paste(rect, (padding + x * size, padding + y * size))
            x += 1

    return image.crop((0, 0, 2 * padding + w * size, 2 * padding + h * size))
