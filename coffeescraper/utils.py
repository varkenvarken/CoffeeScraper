# SPDX-License-Identifier: GPL-3.0-or-later

import os

def get_env(name:str, default=None) -> str|list|None:
    env_value = os.environ.get(name)
    if env_value is None or env_value == "":
        return default

    if "," in env_value:
        return [item.strip() for item in env_value.split(",")]
    else:
        return env_value


def get_secret(filename: str) -> str:
    try:
        with open(filename) as f:
            return f.readline().strip()
    except FileNotFoundError:
        return None

def get_secret_file(filename: str) -> str:
    try:
        with open(filename) as f:
            return "".join(f.readlines())
    except FileNotFoundError:
        return None