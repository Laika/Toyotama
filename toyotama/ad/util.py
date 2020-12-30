from functools import singledispatch

import requests
from toyotama.util.log import info


@singledispatch
def submit_flag(flags, url, token):
    raise TypeError("flag must be str or list.")


@submit_flag.register(list)
def submit_flag_list(flags, url, token):
    header = {
        "x-api-key": token,
    }
    for flag in flags:
        data = {
            "flag": flag,
        }
        response = requests.post(url, data=data, headers=header)
        info(response.text)


@submit_flag.register(str)
def submit_flag_str(flag, url, token):
    header = {
        "x-api-key": token,
    }
    data = {
        "flag": flag,
    }
    response = requests.post(url, data=data, headers=header)
    info(response.text)
