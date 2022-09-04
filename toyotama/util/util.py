import code
from functools import singledispatch
from itertools import zip_longest

from toyotama.util.log import get_logger

logger = get_logger()


class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, data):
        if isinstance(data, dict):
            for key, value in data.items():
                if hasattr(value, "keys"):
                    value = DotDict(value)
                if isinstance(value, list):
                    self[key] = DotDict(value)
                else:
                    self[key] = value
        elif isinstance(data, list):
            for i, v in enumerate(data):
                self[i] = DotDict(v)


class MarkdownTable:
    def __init__(self, header=None, rows=None):
        self.__header = header or ()
        self.__rows = rows or []

    @property
    def header(self):
        return self.__header

    @header.setter
    def header(self, header):
        self.__header = header

    @property
    def rows(self):
        return self.__rows

    @rows.setter
    def rows(self, rows):
        self.__rows = rows

    def __add__(self, other):
        assert self.header == other.header, "The headers don't match."
        return self.__rows + other.__rows

    def __iadd__(self, other):
        assert self.header == other.header, "The headers don't match."
        self.__rows += other.__rows
        return self

    def __get_max_lengths(self):
        array = [self.header] + self.rows
        max_lengths = [max(len(str(s)) for s in ss) for ss in zip_longest(*array, fillvalue="")]
        return max_lengths

    def __get_printable_row(self, row):
        max_lengths = self.__get_max_lengths()
        return "| " + " | ".join((f"{r:<{m}}" for r, m in zip_longest(row, max_lengths, fillvalue=""))) + " |"

    def __get_printable_header(self):
        return self.__get_printable_row(self.header)

    def __get_printable_border(self):
        max_lengths = self.__get_max_lengths()
        return "| " + " | ".join("-" * length for length in max_lengths) + " |"

    def __get_table(self):
        lines = []
        if self.header:
            lines.append(self.__get_printable_header())
            lines.append(self.__get_printable_border())

        for row in self.rows:
            lines.append(self.__get_printable_row(row))

        return lines

    def dump(self):
        lines = self.__get_table()
        return "\n".join(lines)

    def show(self):
        lines = self.__get_table()
        for line in lines:
            print(line)


def interact(symboltable):
    """Switch to interactive mode

    Parameters
    ----------
        symboltable: dict
            The symboltable when this function is called.

    Returns
    -------
    None

    Examples
    --------
    a = 5 + 100
    interact(globals())

    (InteractiveConsole)
    >>> a
    105
    """

    code.interact(local=symboltable)


def printv(symboltable, *args):
    """Show the value and its type

    Parameters
    ----------
        symboltable: dict
            The symboltable when this function is called.

        *args
            The variable to show


    Returns
    -------
    None

    Examples
    --------
    >>> a = 5 + 100
    >>> b = 0x1001
    >>> system_addr = 0x08080808
    >>> s = 'hoge'
    >>> show_variables(globals(), a, b, system_addr, s)

    [+] a            <int>: 105
    [+] b            <int>: 4097
    [+] system_addr  <int>: 0x8080808
    [+] s            <str>: hoge
    """

    def getvarname(var, symboltable, error=None):
        for k, v in symboltable.items():
            if id(v) == id(var):
                return k
        if error == "Exception":
            raise ValueError("undefined function is mixed in subspace?")

    names = [getvarname(var, symboltable) for var in args]
    maxlen_name = max([len(name) for name in names]) + 1
    maxlen_type = max([len(type(value).__name__) for value in args]) + 3
    for name, value in zip(names, args):
        typ = f"<{type(value).__name__}>"
        if name.endswith("_addr"):
            logger.info(f"{name.ljust(maxlen_name)}{typ.rjust(maxlen_type)}: {value:#x}")
        else:
            logger.info(f"{name.ljust(maxlen_name)}{typ.rjust(maxlen_type)}: {value}")


@singledispatch
def extract_flag(s, head="{", tail="}", unique=True):
    """Extract flags from a string

    Parameters
    ----------
    s: str or bytes
        Find flags from this string

    head: str
        The head of flag format

    tail: str
        The tail of flag format


    Returns
    -------
    list
        The list of flags found in `s`

    """

    raise TypeError("s must be str or bytes.")


@extract_flag.register(str)
def extract_flag_str(s, head="{", tail="}", unique=True):
    import re

    patt = f"{head}.*?{tail}"
    comp = re.compile(patt)
    flags = re.findall(comp, s)
    if unique:
        flags = set(flags)
    if not flags:
        logger.error(f"the pattern {head}.*?{tail} does not exist.")
        return None
    return flags


@extract_flag.register(bytes)
def extract_flag_bytes(s, head="{", tail="}", unique=True):
    import re

    patt = f"{head}.*?{tail}".encode()
    comp = re.compile(patt)
    flags = re.findall(comp, s)
    if unique:
        flags = set(flags)
    if not flags:
        logger.error(f"The pattern {head}.*?{tail} does not exist.")
        return None
    return flags


def random_string(
    length,
    plaintext_space="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    byte=True,
):
    """Generate random string

    Parameters
    ----------
    length: int
        Length of random string

    plaintext_space: iterable
        Each character is picked from `plaintext_space`


    Returns
    -------
    str
        Randomly picked string

    Examples
    --------
    >>> random_string(10, 'abcdefghijklmnopqrstuvwxyz')
    'jzhmajvqje'
    >>> random_string(10, 'abcdefghijklmnopqrstuvwxyz')
    'aghlqvucdf'
    """

    from random import choices

    rnd = choices(plaintext_space, k=length)
    if isinstance(plaintext_space, bytes):
        rnd = bytes(rnd)
    if isinstance(plaintext_space, str):
        rnd = "".join(rnd)
    return rnd


def int_to_string(x, byte=False):
    """Convert integer to string

    Parameters
    ----------
    x: int
        Integer

    byte: bool
        Keep it bytes or not

    Returns
    -------
    str (or bytes)
        Result

    Examples
    --------
    >>> int_to_string(8387236825053623156)
    'testtest'
    >>> int_to_string(8387236825053623156, byte=True)
    b'testtest'
    """

    res = bytes.fromhex(format(x, "x"))
    if not byte:
        res = res.decode()
    return res


@singledispatch
def string_to_int(s):
    """Convert string or bytes to integer

    Parameters
    ----------
    s: str (or bytes)
        String

    Returns
    -------
    int
        Result

    Examples
    --------
    >>> string_to_int('testtest')
    8387236825053623156
    >>> string_to_int(b'testtest')
    8387236825053623156
    """

    raise TypeError("s must be str or bytes.")


@string_to_int.register(str)
def string_to_int_str(s):
    return int.from_bytes(s.encode(), "big")


@string_to_int.register(bytes)
def string_to_int_bytes(s):
    return int.from_bytes(s, "big")


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
    from PIL import Image, ImageDraw

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
