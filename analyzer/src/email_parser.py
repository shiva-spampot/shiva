import json
import email.message
import os.path
from email import parser as email_parser
import hashlib


class EmailParser(object):
    def __init__(self, queue_dir):
        self.queue_dir = queue_dir
        self.attachments_dir = os.path.join(self.queue_dir, "attachments")
        os.makedirs(self.attachments_dir, exist_ok=True)

    @staticmethod
    def _parse_headers(message: email.message.Message) -> dict:
        headers = {}
        for key, value in message.items():
            headers[key] = value

        return headers

    def _parse_attachment(self, message_part: email.message.Message) -> dict:
        attachment_info = {
            "file_name": message_part.get_filename(),
            "content_type": message_part.get_content_type()
        }

        file_content = message_part.get_payload(decode=True)
        if file_content:
            attachment_info["file_sha256"] = hashlib.sha256(file_content).hexdigest()
            file_path = os.path.join(self.attachments_dir, attachment_info["file_sha256"])
            with open(file_path, "wb") as fp:
                fp.write(file_content)
            attachment_info["file_path"] = file_path
            return attachment_info

        return {}

    def parse(self, email_key: str) -> dict:
        parsed_email = {}

        email_path = f"{self.queue_dir}/{email_key}.eml"
        meta_path = f"{self.queue_dir}/{email_key}.meta"

        parser = email_parser.Parser()
        with open(email_path) as fp:
            message = parser.parse(fp)

        with open(meta_path) as fp:
            parsed_email.update(json.load(fp))

        parsed_email["subject"] = message["subject"]
        parsed_email["headers"] = self._parse_headers(message)
        parsed_email["body"] = ""
        parsed_email["attachments"] = []

        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue

            if part.get_content_type() in ["text/plain", "text/html"]:
                parsed_email["body"] += part.get_payload(decode=True).decode()

            elif part.get_content_disposition() == "attachment":
                attachment_info = self._parse_attachment(part)
                if attachment_info:
                    parsed_email["attachments"].append(attachment_info)

        return parsed_email
