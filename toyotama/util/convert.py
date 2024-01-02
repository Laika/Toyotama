from functools import singledispatch

from PIL import Image, ImageDraw

from .log import get_logger

logger = get_logger()


def to_block(x: bytes, block_size: int = 16) -> list[bytes]:
    return [x[i : i + block_size] for i in range(0, len(x), block_size)]


def b64_padding(s: str | bytes) -> str | bytes:
    if isinstance(s, str):
        s += "=" * (-len(s) % 4)
        return s
    elif isinstance(s, bytes):
        s += b"=" * (-len(s) % 4)
        return s
    else:
        raise TypeError("s must be str or bytes")


def binary_to_image(
    data,
    padding: int = 5,
    size: int = 5,
    inverted: bool = False,
    image_size: tuple[int, int] = (1000, 1000),
):
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
            if (pixel == "1") ^ inverted:
                image.paste(rect, (padding + x * size, padding + y * size))
            x += 1

    return image.crop((0, 0, 2 * padding + w * size, 2 * padding + h * size))
