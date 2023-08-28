# SPDX-License-Identifier: GPL-3.0-or-later

"""
Module for uploading files via SFTP using Paramiko.

This module provides a function to upload files to a remote server using the SFTP protocol
with the help of the Paramiko library. The function reads necessary connection information
from secret files and performs the upload operation.

Dependencies:
    - paramiko
    - .utils (from the same package)

Functions:
    upload_file_via_sftp(
        hostfile: str,
        usernamefile: str,
        passwordfile: str,
        local_file_path: str,
        remote_file_path: str,
    ) -> None:
        Uploads a local file to a remote server via SFTP using provided connection details.
        Skips the upload if DRYRUN environment variable is set.

    Note: Ensure the necessary dependencies are installed before using this module.
"""
import logging
import paramiko

from .utils import get_secret, get_env


def upload_file_via_sftp(
    hostfile: str,
    usernamefile: str,
    passwordfile: str,
    local_file_path: str,
    remote_file_path: str,
) -> None:
    """
    Upload a file to a remote server via SFTP.

    This function uploads a local file to a remote server using the SFTP protocol.
    It uses connection information provided through secret files, and it prints
    a success message upon successful upload.

    Args:
        hostfile (str): Path to the secret file containing the host information.
        usernamefile (str): Path to the secret file containing the username.
        passwordfile (str): Path to the secret file containing the password.
        local_file_path (str): Path to the local file to be uploaded.
        remote_file_path (str): Path where the file should be uploaded on the remote server.

    Returns:
        None: This function does not return any value. It prints relevant messages.
    """

    if get_env("DRYRUN") is not None:
        logging.info(f"sftp upload of {local_file_path} skipped")
        return

    host = get_secret(hostfile)
    username = get_secret(usernamefile)
    password = get_secret(passwordfile)

    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_file_path, remote_file_path)

    sftp.close()
    transport.close()

    logging.info(
        f"File '{local_file_path}' uploaded to '{host}/{remote_file_path}' successfully"
    )
