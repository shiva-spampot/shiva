import asyncio
import datetime
import json
import logging
import os
import random
import re
import time
import uuid
from aiosmtpd.controller import Controller
from aiosmtpd.smtp import AuthResult, LoginPassword
from aiosmtpd.smtp import SMTP as SMTPServer
from aiosmtpd.smtp import Envelope as SMTPEnvelope
from aiosmtpd.smtp import Session as SMTPSession

import config


class Authenticator:
    def __call__(
        self,
        server: SMTPServer,
        session: SMTPSession,
        envelope: SMTPEnvelope,
        mechanism: str,
        auth_data,
    ) -> AuthResult:
        # TODO Store credentials in a DB/config.
        test_passwd = b"password"
        test_username = b"username"

        resp = AuthResult(success=False, handled=False)
        if mechanism not in ("LOGIN", "PLAIN"):
            return resp
        if not isinstance(auth_data, LoginPassword):
            return resp

        username = auth_data.login
        password = auth_data.password
        if username == test_username and password == test_passwd:
            resp = AuthResult(success=True)

        return resp


class ShivaHandler:
    async def handle_DATA(
        self,
        server: SMTPServer,
        session: SMTPSession,
        envelope: SMTPEnvelope,
    ):
        # Handle incoming email data
        peer = session.peer
        mail_from = envelope.mail_from
        rcpt_tos = envelope.rcpt_tos
        data = envelope.content  # type: bytes

        email_error = self.validate_emails(mail_from, rcpt_tos)
        if email_error:
            return email_error

        self._process_spam_message(peer, mail_from, rcpt_tos, data)
        self._random_delay()

        return "250 OK"

    def validate_emails(self, mail_from: str, rcpt_tos: list) -> str:
        if not self.is_valid_email(mail_from):
            return "554 Invalid sender address"

        for recipient in rcpt_tos:
            if not self.is_valid_email(recipient):
                return f"554 Invalid recipient address: {recipient}"

    def _process_spam_message(self, peer, mailfrom, rcpttos, data):
        print("Received spam, parsing now.")
        spam_meta_details = {}
        client_info = self._parse_client_info(peer)
        if client_info:
            spam_meta_details.update(client_info)

        spam_meta_details["sender"] = mailfrom
        spam_meta_details["recipients"] = rcpttos
        spam_meta_details["sensor_name"] = config.SENSOR_NAME
        spam_meta_details["index_ts"] = self.get_current_dt()

        print(spam_meta_details)

        self._write_files(spam_meta_details, data)

    @staticmethod
    def _parse_client_info(peer: tuple):
        try:
            host, port = peer
            return {"client_addr": host, "client_port": port}
        except Exception as e:
            print(f"Failed to parsed peer info: {e}")

    @staticmethod
    def _write_files(meta_details: dict, data: bytes):
        unique_name = uuid.uuid4().hex
        meta_file = os.path.join(config.QUEUE_DIR, f"{unique_name}.meta")
        eml_file = os.path.join(config.QUEUE_DIR, f"{unique_name}.eml")

        print("Writing metadata file.")
        with open(meta_file, "w") as fp:
            json.dump(meta_details, fp, indent=4)

        print("Writing raw eml file.")
        with open(eml_file, "wb") as fp:
            fp.write(data)

    @staticmethod
    def _random_delay():
        time.sleep(random.uniform(0.1, 2))

    @staticmethod
    def get_current_dt():
        dt = datetime.datetime.now(datetime.timezone.utc)
        return dt.isoformat()

    def is_valid_email(self, email):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None


if __name__ == "__main__":
    LOG_FORMAT = "%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d [+] %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    os.makedirs(config.QUEUE_DIR, exist_ok=True)
    handler = ShivaHandler()
    controller = Controller(
        handler,
        hostname="localhost",
        port=2525,
        authenticator=Authenticator(),
        auth_required=True,
        auth_require_tls=False,
    )
    controller.start()

    try:
        print("SMTP server running on localhost:2525. Press Ctrl+C to stop.")
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
