from sqlalchemy import Column, BIGINT, ForeignKey, String, CHAR, Text, DateTime, func
from helpers.common import get_utc_datetime
from models.base import Base, CRUDBase, TimeStampedMixin


class EmailCampaigns(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "email_campaigns"

    id = Column(BIGINT, primary_key=True, index=True)
    body_sha256 = Column(
        CHAR(64),
        index=True,
        comment="SHA256 hash of the normalized contents",
        nullable=False,
    )
    body_ssdeep = Column(Text, comment="SSDEEP of the normalized content")
    subject = Column(Text)
    body_size = Column(BIGINT)
    campaign_name = Column(
        String, comment="Optional: a name or identifier for the campaign"
    )
    first_seen_at = Column(
        DateTime, default=get_utc_datetime, server_default=func.now()
    )
    last_seen_at = Column(DateTime, default=get_utc_datetime, server_default=func.now())
    email_body = Column(Text, nullable=False)
    raw_email_id = Column(BIGINT, ForeignKey("raw_emails.id"))
