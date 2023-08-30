from unittest.mock import patch
from coffeescraper.sftp import upload_file_via_sftp
import os
import pathlib

h = pathlib.Path("/tmp/hostfile")
u = pathlib.Path("/tmp/username")
p = pathlib.Path("/tmp/password")
l = pathlib.Path("/tmp/localfile")
r = pathlib.Path("/remote-file")

def create_files():
    with open(h, "w") as file:
        file.write("ssh.example.org")
    with open(u, "w") as file:
        file.write("exampleuser")
    with open(p, "w") as file:
        file.write("examplepassword")
    with open(l, "w") as file:
        file.write("oink,gnerk,groink")


class TestSFTP:
    @patch("paramiko.Transport", autospec=True)
    @patch("paramiko.SFTPClient", autospec=True)
    def test_sftp_dryrun(self, mockclient, mocktransport):
        create_files()
        os.environ["DRYRUN"] = "1"
        upload_file_via_sftp(h, u, p, l, "/remote-file")
        mocktransport.assert_not_called()
        mockclient.from_transport.assert_not_called()
        mockclient.put.assert_not_called()
        mockclient.close.assert_not_called()
        mocktransport.close.assert_not_called()

    @patch("paramiko.Transport", autospec=True)
    @patch("paramiko.SFTPClient", autospec=True)
    def test_sftp_upload(self, mockclient, mocktransport):
        create_files()
        if "DRYRUN" in os.environ:
            del os.environ["DRYRUN"]
        upload_file_via_sftp(h, u, p, l, r)
        mocktransport.assert_called_once_with(("ssh.example.org",22))
        mocktransportinstance = mocktransport.return_value
        mocktransportinstance.connect.assert_called_once_with(username="exampleuser",password="examplepassword")

        mockclient.from_transport.assert_called_once_with(mocktransportinstance)
        mockclientinstance = mockclient.from_transport.return_value
        
        mockclientinstance.put.assert_called_with(l,r)
        mockclientinstance.close.assert_called_once()
        mocktransportinstance.close.assert_called_once()

