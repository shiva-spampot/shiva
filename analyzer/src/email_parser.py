import json
import email.message
import os.path
from email import parser as email_parser
import hashlib
import re
import ssdeep
import magic

file_magic = magic.Magic(mime=True)


class EmailParser(object):
    def __init__(self, queue_dir):
        self.queue_dir = queue_dir

    @staticmethod
    def _parse_headers(message: email.message.Message) -> dict:
        headers = {}
        for key, value in message.items():
            headers[key] = value

        return headers

    def _parse_attachment(self, message_part: email.message.Message) -> dict:
        attachment_info = {"file_name": message_part.get_filename()}

        file_content = message_part.get_payload(decode=True)
        if file_content:
            attachment_info["content_type"] = (
                self._get_file_type(file_content) or message_part.get_content_type()
            )
            attachment_info["file_sha256"] = hashlib.sha256(file_content).hexdigest()
            attachment_info["content"] = file_content
            attachment_info["file_size"] = len(file_content)
            extension_name = self._get_file_extension(attachment_info["file_name"])
            if extension_name:
                attachment_info["file_extension"] = extension_name

            return attachment_info

        return {}

    def _get_file_type(self, payload):
        try:
            return file_magic.from_buffer(payload)
        except Exception as e:
            return None

    def _get_file_extension(self, filename: str) -> str:
        extension_name = ""
        if not filename:
            return extension_name
        if "." in filename:
            extension_name = filename.split(".")[-1]

        return extension_name

    def parse(self, email_key: str) -> dict:
        parsed_email = {}

        email_path = f"{self.queue_dir}/{email_key}.eml"
        meta_path = f"{self.queue_dir}/{email_key}.meta"

        parser = email_parser.Parser()
        with open(email_path) as fp:
            parsed_email["raw_email"] = fp.read()
            fp.seek(0)
            message = parser.parse(fp)

        with open(meta_path) as fp:
            parsed_email.update(json.load(fp))
            parsed_email["sender"] = self._normalizer_content(parsed_email["sender"])
            parsed_email["recipients"] = list(
                set(map(self._normalizer_content, parsed_email["recipients"]))
            )

        parsed_email["subject"] = message["subject"]
        parsed_email["headers"] = self._parse_headers(message)
        parsed_email["body"] = ""
        parsed_email["body_size"] = 0
        parsed_email["attachments"] = []
        parsed_email["urls"] = []

        for part in message.walk():
            if part.get_content_maintype() == "multipart":
                continue

            if part.get_content_type() in ["text/plain", "text/html"]:
                tmp_string = (
                    part.get_payload()
                    .encode()
                    .decode("unicode-escape")
                    .encode("latin1")
                    .decode("utf-8")
                )
                parsed_email["body"] += tmp_string

            elif part.get_content_disposition() == "attachment":
                attachment_info = self._parse_attachment(part)
                if attachment_info:
                    parsed_email["attachments"].append(attachment_info)

        if parsed_email["body"]:
            body = parsed_email["body"].encode()
            parsed_email["body_size"] = len(body)
            parsed_email["body_sha256"] = hashlib.sha256(body).hexdigest()

            # SSDEEP needs data to be larger than 4KB for generating meaningful hashes.
            if len(body) > 4096:
                parsed_email["body_ssdeep"] = ssdeep.hash(body)

            parsed_email["urls"] = self.extract_urls(body.decode())

        return parsed_email

    def _normalizer_content(self, record: str):
        return record.lower().strip()

    def extract_urls(self, text: str) -> list:
        if not text:
            return []

        regex = r"https?://(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?(?:/[^\s<>\"#]*)?(?:\?[^\s<>\"#]*)?(?:#[^\s<>\"#]*)?|www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s<>\"#]*)?(?:\?[^\s<>\"#]*)?(?:#[^\s<>\"#]*)?"
        urls = set()
        for url in set(re.findall(regex, text)):
            if not url.startswith("http"):
                continue
            urls.add(url)

        return list(urls)
