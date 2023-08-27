# SPDX-License-Identifier: GPL-3.0-or-later

import paramiko

from .utils import get_secret, get_env


def upload_file_via_sftp(
    hostfile: str,
    usernamefile: str,
    passwordfile: str,
    local_file_path: str,
    remote_file_path: str,
) -> None:
    
    if get_env("DRYRUN") is not None:
        print(f"sftp upload of {local_file_path} skipped")
        return
    
    host = get_secret(hostfile)
    username = get_secret(usernamefile)
    password = get_secret(passwordfile)

    try:
        transport = paramiko.Transport((host, 22))
        transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_file_path, remote_file_path)

        sftp.close()
        transport.close()

        print(
            f"File '{local_file_path}' uploaded to '{remote_file_path}' successfully."
        )
    except Exception as e:
        print(f"An error occurred: {e}")
