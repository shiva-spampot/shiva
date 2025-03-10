from datetime import datetime
import hashlib
import os
import traceback
from urllib.parse import urlparse
import uuid
from sqlalchemy import select
import ssdeep
from storages.local import LocalStorage
from helpers.factory import get_storage_backend
from models.recipients_mapping import RecipientsMapping
from config import config
from models.attachments import Attachments
from models.attachment_mapping import AttachmentMapping
from models.campaigns import Campaigns
from models.url_mapping import URLMapping
from models.urls import URLs
from models.emails import Emails
from models.raw_emails import RawEmails
from models.recipients import Recipients
from models.senders import Senders
from integrations import virustotal
import email_parser
from sqlalchemy.orm import Session
import logging as logger


logger.getLogger(__name__)


class SHIVAAnalyzer(object):
    def __init__(self, db: Session, config):
        self._config = config
        self.db = db
        self.archive_dir = self._get_archive_path()
        self._parser = email_parser.EmailParser(self._config["shiva"]["queue_dir"])
        self.storage = get_storage_backend()
        self.local_storage = LocalStorage(self._config["shiva"]["queue_dir"])
        # self._vt_client = virustotal.VTLookup(config.VT_API_KEY)

    def _get_archive_path(self):
        archive_dir = self._config["shiva"]["archive_dir"]
        if archive_dir:
            if not os.path.exists(archive_dir):
                try:
                    os.mkdir(archive_dir)
                except Exception as e:
                    logger.error(f"Failed to create archive dir: {e}")
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
        try:
            campaign_obj = self.get_or_create_campaign()
            email_objs = self.get_or_create_email(campaign_obj)
            self.process_urls(email_objs)

            self.process_attachments(email_objs)
        except:
            logger.error(f"Failed to process file: {file_key}", exc_info=True)
            email_path = f'{self._config["shiva"]["queue_dir"]}/{file_key}.eml'
            meta_path = f'{self._config["shiva"]["queue_dir"]}/{file_key}.meta'

            failed_folder_path = "failed"
            with open(email_path) as f:
                self.local_storage.save(
                    f"{failed_folder_path}/{file_key}.eml", f.read()
                )

            with open(meta_path) as f:
                self.local_storage.save(
                    f"{failed_folder_path}/{file_key}.meta", f.read()
                )

            self.local_storage.save(
                f"{failed_folder_path}/{file_key}.err", traceback.format_exc()
            )

    def get_or_create_campaign(self):
        campaign = self.find_campaign()
        if campaign:
            return campaign

        tmp_raw_file_name = f"raw_emails/{uuid.uuid4().hex}.eml"
        file_path = self.storage.save(tmp_raw_file_name, self.parse_result["raw_email"])
        raw_email_obj = RawEmails.create(self.db, data=file_path)

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

        campaign_obj = Campaigns.create(self.db, **record)
        campaign_name = f"Campaign {campaign_obj.id}"
        campaign_obj = Campaigns.update(self.db, campaign_obj.id, name=campaign_name)

        return campaign_obj

    def get_or_create_email(self, campaign_obj: Campaigns):
        sender = self.parse_result["sender"]
        sender_obj = self.get_or_create_sender(sender)

        record = {
            "campaign_id": campaign_obj.id,
            "sender_id": sender_obj.id,
            "subject": self.parse_result["subject"],
            "send_at": datetime.fromisoformat(self.parse_result["index_ts"]),
            "sender_ip": self.parse_result["client_addr"],
            "headers": self.parse_result["headers"],
        }

        if self.parse_result["headers"] and self.parse_result["headers"].get(
            "User-Agent"
        ):
            record["user_agent"] = self.parse_result["headers"].get("User-Agent")

        email_obj = Emails.create(self.db, **record)
        for recipient in self.parse_result["recipients"]:
            receiver_obj = self.get_or_create_receiver(recipient)

            record = {"email_id": email_obj.id, "recipient_id": receiver_obj.id}

            RecipientsMapping.create(self.db, **record)

        return email_obj

    def find_campaign(self):
        body_sha256 = self.parse_result.get("body_sha256")
        body_ssdeep = self.parse_result.get("body_ssdeep")
        body_size = self.parse_result.get("body_size")
        query = {"body_sha256": body_sha256}
        campaign_obj = Campaigns.get_one_or_none(self.db, query)
        if campaign_obj:
            return campaign_obj

        campaign_id = self._check_ssdeep_campaign_body(body_ssdeep, body_size)
        if campaign_id:
            return campaign_id

    def _check_ssdeep_campaign_body(self, body_ssdeep: str, body_size: int):
        if not body_ssdeep:
            return

        difference = 0.13 * body_size
        min_value = body_size - difference
        max_value = body_size + difference
        query = select(Campaigns.id, Campaigns.body_ssdeep).filter(
            Campaigns.body_size.between(
                min_value,
                max_value,
            ),
            Campaigns.body_ssdeep.is_not(None),
        )
        capmaigns = Campaigns.get_all(self.db, query)
        ssdeep_similarity_threshold = int(
            config["shiva"]["ssdeep_similarity_threshold"]
        )
        for result in capmaigns:
            score = ssdeep.compare(body_ssdeep, result.body_ssdeep)
            if score >= ssdeep_similarity_threshold:
                return result

    def process_urls(self, email_obj: Emails):
        for url in self.parse_result["urls"]:
            url_obj = self.get_or_create_email_url(url)
            try:
                URLMapping.create(
                    self.db,
                    email_id=email_obj.id,
                    url_id=url_obj.id,
                )
            except:
                pass

    def process_attachments(self, email_obj: Emails):
        for attachment in self.parse_result["attachments"]:
            attachment_obj = self.get_or_create_attachment(attachment)
            try:
                AttachmentMapping.create(
                    self.db,
                    email_id=email_obj.id,
                    attachment_id=attachment_obj.id,
                )
            except:
                pass

    def get_or_create_email_url(self, url: str) -> URLs:
        url_sha256 = hashlib.sha256(url.encode()).hexdigest()
        query = {"url_sha256": url_sha256}
        email_url_obj = URLs.get_one_or_none(self.db, query)
        if email_url_obj:
            return email_url_obj

        url_obj = urlparse(url)
        record = {
            "url": url,
            "url_sha256": url_sha256,
            "domain": url_obj.hostname,
        }
        email_url_obj = URLs.create(self.db, **record)

        return email_url_obj

    def get_or_create_attachment(self, attachment: dict) -> Attachments:

        query = {"file_sha256": attachment["file_sha256"]}
        attachment_obj = Attachments.get_one_or_none(self.db, query)
        if attachment_obj:
            return attachment_obj

        record = {
            "file_name": attachment["file_name"],
            "file_sha256": attachment["file_sha256"],
            "file_type": attachment["content_type"],
            "file_size": attachment["file_size"],
        }

        file_name = f"attachments/{uuid.uuid4().hex}_{attachment['file_name']}"

        file_path = self.storage.save(file_name, attachment["content"])
        record["attachment_file_url"] = file_path
        if "file_extension" in attachment:
            record["file_extension"] = attachment["file_extension"]

        attachment_obj = Attachments.create(self.db, **record)

        return attachment_obj

    def get_or_create_sender(self, email: str) -> Senders:
        query = {"email": email}

        email_obj = Senders.get_one_or_none(self.db, query)
        if email_obj:
            return email_obj

        email_obj = Senders.create(self.db, email=email, domain=email.split("@")[-1])
        return email_obj

    def get_or_create_receiver(self, email: str) -> Recipients:
        query = {"email": email}

        email_obj = Recipients.get_one_or_none(self.db, query)
        if email_obj:
            return email_obj

        email_obj = Recipients.create(self.db, email=email, domain=email.split("@")[-1])

        return email_obj
