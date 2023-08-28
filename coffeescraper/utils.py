# SPDX-License-Identifier: GPL-3.0-or-later

"""
This module provides utility functions for retrieving environment variables and secrets.

These functions assist in accessing environment variables and secret files, providing default
values or handling missing values appropriately.

Functions:
    get_env(name, default=None) -> str|list|None:
        Retrieve the value of an environment variable.
    get_secret(filename) -> str:
        Retrieve the content of a secret file.
    get_secret_file(filename) -> str:
        Retrieve the content of a secret file as a single string.

"""

import os

def get_env(name:str, default=None) -> str|list[str]|None:
    """
    Retrieve the value of an environment variable.

    If the value is a comma separated list, a list of string is returned
    Args:
        name (str): The name of the environment variable.
        default: Default value to return if the variable is not set or empty.

    Returns:
        str | list[str] | None: The value of the environment variable, or the default value if not set or empty.
    """
    
    env_value = os.environ.get(name)
    if env_value is None or env_value == "":
        return default

    if "," in env_value:
        return [item.strip() for item in env_value.split(",")]
    else:
        return env_value


def get_secret(filename: str) -> str|None:
    """
    Retrieve the first line of a file.

    Leading and trailing whitespace is removed.

    Args:
        filename (str): The path to the secret file.

    Returns:
        str|None: The first line of the secret file, or None if the file is not found.
    """
    
    try:
        with open(filename) as f:
            return f.readline().strip()
    except FileNotFoundError:
        return None

def get_secret_file(filename: str) -> str|None:
    """
    Retrieve the contents of a secret file as a single string.

    Args:
        filename (str): The path to the secret file.

    Returns:
        str|None: The contents of the secret file as a single string, or None if the file is not found.
    """
    
    try:
        with open(filename) as f:
            return "".join(f.readlines())
    except FileNotFoundError:
        return None