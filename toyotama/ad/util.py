"""Attack-and-Defense utility module
"""

from functools import singledispatch

import requests

from toyotama.util.log import Logger

log = Logger()


@singledispatch
def submit_flag(flags, url: str, token: str):
    """Submit flags

    Args:
        flags (list or str): Flags you've got.
          url         (str): A URL.
        token         (str): A token needed to submit.

    Returns:
        None
    """
    raise TypeError("flag must be str or list.")


@submit_flag.register(list)
def submit_flag_list(flags: list[str], url: str, token: str):
    header = {
        "x-api-key": token,
    }
    for flag in flags:
        data = {
            "flag": flag,
        }
        response = requests.post(url, data=data, headers=header)
        log.information(response.text)


@submit_flag.register(str)
def submit_flag_str(flag: str, url: str, token: str):
    header = {
        "x-api-key": token,
    }
    data = {
        "flag": flag,
    }
    response = requests.post(url, data=data, headers=header)
    log.information(response.text)
