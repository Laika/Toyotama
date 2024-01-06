import base64
import os

from toyotama.util.log import get_logger

logger = get_logger(__name__, os.environ.get("TOYOTAMA_LOG_LEVEL", "INFO"))


def copy_to_clipboard(string: bytes) -> None:
    b64_string: str = base64.b64encode(string).decode()
    print(f"\x1b]52;c;{b64_string}\a")


if __name__ == "__main__":
    copy_to_clipboard(b"Hello World")
