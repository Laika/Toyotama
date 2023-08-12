"""Attack-and-Defense utility module
"""

import requests

from ..util.log import get_logger

logger = get_logger()


def submit_flag(flag: str, url: str, token: str):
    header = {
        "x-api-key": token,
    }
    data = {
        "flag": flag,
    }
    response = requests.post(url, data=data, headers=header)
    logger.info(response.text)


def submit_flags(flags: list[str], url: str, token: str):
    for flag in flags:
        submit_flag(flag, url, token)
