from sqlalchemy import Column, BIGINT, DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import INET
from models.base import Base, CRUDBase, TimeStampedMixin


class Emails(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "emails"

    id = Column(BIGINT, primary_key=True, index=True)
    message_id = Column(String, nullable=False, comment="SMTP message ID")
    subject = Column(Text)
    sender_id = Column(BIGINT, ForeignKey("senders.id"), nullable=False)
    receiver_id = Column(BIGINT, ForeignKey("receivers.id"), nullable=False)
    campaign_id = Column(
        BIGINT, ForeignKey("email_campaigns.id"), nullable=False
    )
    send_at = Column(DateTime)
    sender_ip = Column(INET, nullable=False)
    count = Column(Integer, default=1, server_default="1")
