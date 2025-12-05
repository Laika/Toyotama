import base64
from logging import getLogger

logger = getLogger(__name__)


def copy_to_clipboard(string: bytes) -> None:
    b64_string: str = base64.b64encode(string).decode()

    logger.info(f"Copy to clipboard: {string}")
    print(f"\x1b]52;c;{b64_string}\a")
