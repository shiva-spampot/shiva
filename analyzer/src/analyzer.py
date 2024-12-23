from datetime import datetime
import hashlib
import os
from typing import List
from urllib.parse import urlparse
import uuid
from sqlalchemy import select
import ssdeep
import config
from models.attachments import Attachments
from models.email_attachment_mapping import EmailAttachmentMapping
from models.email_campaigns import EmailCampaigns
from models.email_url_mapping import EmailURLMapping
from models.email_urls import EmailURLs
from models.emails import Emails
from models.raw_emails import RawEmails
from models.receivers import Receivers
from models.senders import Senders
from integrations import virustotal
import email_parser
from sqlalchemy.orm import Session


class SHIVAAnalyzer(object):
    def __init__(self, db: Session, config):
        self._config = config
        self.db = db
        self.archive_dir = self._get_archive_path()
        self._parser = email_parser.EmailParser(self._config.QUEUE_DIR)
        # self._vt_client = virustotal.VTLookup(config.VT_API_KEY)

    def _get_archive_path(self):
        archive_dir = self._config.ARCHIVE_DIR
        if archive_dir:
            if not os.path.exists(self.archive_dir):
                try:
                    os.mkdir(self.archive_dir)
                except Exception as e:
                    print(f"Failed to create archive dir: {e}")
                    archive_dir = ""
        return archive_dir

    # def parse(self, file_key: str) -> dict:
    #     print(f"Currently parsing {file_key}")
    #     parsed_info = self._parser.parse(file_key)
    #     attachments = parsed_info.get("attachments")
    #     if attachments:
    #         pass
    #         # if self._vt_client:
    #         #     for attachment in attachments:
    #         #         print(f"Checking {attachment['file_sha256']} hash on VT.")
    #         #         if vt_result:
    #         #             attachment["virustotal"] = vt_result

    # return parsed_info

    def run(self, file_key: str):
        self.parse_result = self._parser.parse(file_key)

        campaign_obj = self.get_or_create_campaign()
        email_objs = self.get_or_create_email(campaign_obj)
        self.process_urls(email_objs)

        self.process_attachments(email_objs)

    def get_or_create_campaign(self):
        campaign = self.find_campaign()
        if campaign:
            return campaign

        raw_email_obj = RawEmails.create(self.db, data=self.parse_result["raw_email"])

        record = {
            "email_body": self.parse_result["body"],
            "body_size": self.parse_result["body_size"],
            "body_sha256": self.parse_result["body_sha256"],
            "body_sha256": self.parse_result["body_sha256"],
            "subject": self.parse_result["subject"],
            "first_seen_at": datetime.fromisoformat(self.parse_result["index_ts"]),
            "raw_email_id": raw_email_obj.id,
        }
        if self.parse_result.get("body_ssdeep"):
            record["body_ssdeep"] = self.parse_result["body_ssdeep"]

        return EmailCampaigns.create(self.db, **record)

    def get_or_create_email(self, campaign_obj: EmailCampaigns):
        sender = self.parse_result["sender"]
        sender_obj = self.get_or_create_sender(sender)

        message_id = uuid.uuid4().hex
        email_objs = []
        for recipient in self.parse_result["recipients"]:
            receiver_obj = self.get_or_create_receiver(recipient)
            query = {
                "campaign_id": campaign_obj.id,
                "sender_id": sender_obj.id,
                "receiver_id": receiver_obj.id,
            }
            email_obj = Emails.get_all(self.db, query)
            if email_obj:
                email_obj = email_obj[0]
                counter = email_obj.count + 1
                email_obj = Emails.update(self.db, email_obj.id, count=counter)
            else:
                record = {
                    "message_id": message_id,
                    "campaign_id": campaign_obj.id,
                    "receiver_id": receiver_obj.id,
                    "sender_id": sender_obj.id,
                    "subject" : self.parse_result["subject"],
                    "send_at": datetime.fromisoformat(self.parse_result["index_ts"]),
                    "sender_ip": self.parse_result["client_addr"],
                }
                email_obj = Emails.create(self.db, **record)

            email_objs.append(email_obj)

        return email_objs

    def find_campaign(self):
        body_sha256 = self.parse_result.get("body_sha256")
        body_ssdeep = self.parse_result.get("body_ssdeep")
        body_size = self.parse_result.get("body_size")
        query = {"body_sha256": body_sha256}
        campaign_obj = EmailCampaigns.get_all(self.db, query)
        if campaign_obj:
            return campaign_obj[0]

        campaign_id = self._check_ssdeep_campaign_body(body_ssdeep, body_size)
        if campaign_id:
            return campaign_id

    def _check_ssdeep_campaign_body(self, body_ssdeep: str, body_size: int):
        if not body_ssdeep:
            return

        difference = 0.13 * body_size
        min_value = body_size - difference
        max_value = body_size + difference
        query = select(EmailCampaigns.campaign_id, EmailCampaigns.body_ssdeep).filter(
            EmailCampaigns.email_body.between(
                min_value,
                max_value,
            )
        )
        capmaigns = EmailCampaigns.get_all(self.db, query)
        for result in capmaigns:
            score = ssdeep.compare(body_ssdeep, result["body_ssdeep"])
            if score >= config.SSDEEP_SIMILARITY_THRESHOLD:
                return result["campaign_id"]

    def process_urls(self, email_objs: List[Emails]):
        for url in self.parse_result["urls"]:
            url_obj = self.get_or_create_email_url(url)
            for email_obj in email_objs:
                try:
                    EmailURLMapping.create(
                        self.db,
                        email_id=email_obj.id,
                        url_id=url_obj.id,
                    )
                except:
                    pass

    def process_attachments(self, email_objs: List[Emails]):
        for attachment in self.parse_result["attachments"]:
            attachment_obj = self.get_or_create_attachment(attachment)
            for email_obj in email_objs:
                try:
                    EmailAttachmentMapping.create(
                        self.db,
                        email_id=email_obj.id,
                        attachment_id=attachment_obj.id,
                    )
                except:
                    pass

    def get_or_create_email_url(self, url: str) -> EmailURLs:
        url_sha256 = hashlib.sha256(url.encode()).hexdigest()
        query = {"url_sha256": url_sha256}
        email_url_obj = EmailURLs.get_all(self.db, query)
        if email_url_obj:
            return email_url_obj[0]

        url_obj = urlparse(url)
        record = {
            "url": url,
            "url_sha256": url_sha256,
            "domain": url_obj.hostname,
        }
        email_url_obj = EmailURLs.create(self.db, **record)

        return email_url_obj

    def get_or_create_attachment(self, attachment: dict) -> Attachments:

        query = {"file_sha256": attachment["file_sha256"]}
        attachment_obj = Attachments.get_all(self.db, query)
        if attachment_obj:
            return attachment_obj[0]

        record = {
            "file_name": attachment["file_name"],
            "file_sha256": attachment["file_sha256"],
            "file_type": attachment["content_type"],
            "attachment_file_url": attachment["attachment_file_url"],
            "file_size": attachment["file_size"],
        }
        if "file_extension" in attachment:
            record["file_extension"] = attachment["file_extension"]

        attachment_obj = Attachments.create(self.db, **record)

        return attachment_obj

    def get_or_create_sender(self, email: str) -> Senders:
        query = {"email": email}

        email_obj = Senders.get_all(self.db, query)
        if email_obj:
            email_obj = email_obj[0]
            return email_obj

        email_obj = Senders.create(self.db, email=email, domain=email.split("@")[-1])
        return email_obj

    def get_or_create_receiver(self, email: str) -> Receivers:
        query = {"email": email}

        email_obj = Receivers.get_all(self.db, query)
        if email_obj:
            email_obj = email_obj[0]
            return email_obj

        email_obj = Receivers.create(self.db, email=email, domain=email.split("@")[-1])

        return email_obj
