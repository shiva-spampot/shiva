import datetime
import json
import logging
import os
import random
import re
import time
import uuid
from aiosmtpd.smtp import SMTP as SMTPServer
from aiosmtpd.smtp import Envelope as SMTPEnvelope
from aiosmtpd.smtp import Session as SMTPSession
import config


class ShivaHandler:
    def __init__(self):
        self.__config = config.get_config()
        self.max_email_size = 25 * 1024 * 1024  # 25 MB
        os.makedirs(self.__config["shiva"]["queue_dir"], exist_ok=True)

    async def handle_DATA(
        self,
        server: SMTPServer,
        session: SMTPSession,
        envelope: SMTPEnvelope,
    ):
        # Handle incoming email data
        try:
            peer = session.peer
            mail_from = envelope.mail_from
            rcpt_tos = envelope.rcpt_tos
            data = envelope.content  # type: bytes

            email_error = self.validate_emails(mail_from, rcpt_tos)
            if email_error:
                return email_error

            if len(data) > self.max_email_size:
                # Reject the email if it exceeds the size limit
                return f"552 5.3.4 Message size exceeds the limit ({self.max_email_size} bytes)"

            self._process_spam_message(peer, mail_from, rcpt_tos, data)
            self._random_delay()
        except:
            logging.error("Failed to process the mail", exc_info=True)

        return f"250 Ok: queued as: {uuid.uuid4()}"

    def validate_emails(self, mail_from: str, rcpt_tos: list) -> str:
        if not self.is_valid_email(mail_from):
            return "554 Invalid sender address"

        for recipient in rcpt_tos:
            if not self.is_valid_email(recipient):
                return f"554 Invalid recipient address: {recipient}"

    def _process_spam_message(self, peer, mailfrom, rcpttos, data):
        logging.debug("Received spam, parsing now.")
        spam_meta_details = {}
        client_info = self._parse_client_info(peer)
        if client_info:
            spam_meta_details.update(client_info)

        spam_meta_details["sender"] = mailfrom
        spam_meta_details["recipients"] = rcpttos
        spam_meta_details["sensor_name"] = self.__config["shiva"]["sensor_name"]
        spam_meta_details["index_ts"] = self.get_current_dt()

        self._write_files(spam_meta_details, data)

    @staticmethod
    def _parse_client_info(peer: tuple):
        try:
            host, port = peer
            return {"client_addr": host, "client_port": port}
        except Exception as e:
            logging.error(f"Failed to parsed peer info: {e}")

    def _write_files(self, meta_details: dict, data: bytes):
        unique_name = uuid.uuid4().hex
        folder_path = self.__config["shiva"]["queue_dir"]
        meta_file = os.path.join(folder_path, f"{unique_name}.meta")
        eml_file = os.path.join(folder_path, f"{unique_name}.eml")

        logging.debug("Writing metadata file.")
        with open(meta_file, "w") as fp:
            json.dump(meta_details, fp, indent=4)

        logging.debug("Writing raw eml file.")
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
