from unittest.mock import patch, call
from coffeescraper.smtp import send_message
import os
from random import seed

message = "oink, gnerk, groink"
encoded_message = 'Content-Type: multipart/mixed; boundary="===============1026847926404610461=="\nMIME-Version: 1.0\nFrom: sender@example.org\nTo: recipient@example.org\nSubject: =?utf-8?q?Test?=\n\n--===============1026847926404610461==\nContent-Type: text/plain; charset="us-ascii"\nMIME-Version: 1.0\nContent-Transfer-Encoding: 7bit\n\noink, gnerk, groink\n--===============1026847926404610461==--\n'

class TestSMTP:
    @patch("coffeescraper.smtp.get_secret")
    @patch("smtplib.SMTP_SSL", autospec=True)
    def test_smtp_dryrun(self, mockclient, mockget_secret):
        os.environ["DRYRUN"] = "1"
        send_message(
            "sender@example.org", "recipient@example.org", "Test", message
        )
        mockget_secret.assert_not_called()
        mockclient.assert_not_called()

    @patch("coffeescraper.smtp.get_secret")
    @patch("smtplib.SMTP_SSL", autospec=True)
    def test_smtp_send_message(self, mockclient, mockget_secret):
        if "DRYRUN" in os.environ:
            del os.environ["DRYRUN"]
        mockget_secret.return_value = "aaaa"
        seed(42)  # force the MimeMultipart separator to always be the same
        send_message(
            "sender@example.org", "recipient@example.org", "Test", message
        )
        mockget_secret.assert_has_calls(
            [
                call("/run/secrets/smtp_user"),
                call("/run/secrets/smtp_password"),
                call("/run/secrets/smtp_host"),
            ]
        )
        mockclient.assert_called_with("aaaa", 465)
        mockclientinstance = mockclient.return_value.__enter__.return_value
        mockclientinstance.login.assert_called_once_with("aaaa", "aaaa")
        mockclientinstance.sendmail.assert_called_once_with(
            "sender@example.org", "recipient@example.org",encoded_message
        )
