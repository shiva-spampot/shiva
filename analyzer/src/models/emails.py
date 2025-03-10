from sqlalchemy import Column, BIGINT, DateTime, ForeignKey, String, Text, Integer
from sqlalchemy.dialects.postgresql import INET, JSON
from models.base import Base, CRUDBase, TimeStampedMixin


class Emails(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "emails"

    id = Column(BIGINT, primary_key=True, index=True)
    subject = Column(Text)
    sender_id = Column(BIGINT, ForeignKey("senders.id"), nullable=False)
    campaign_id = Column(BIGINT, ForeignKey("campaigns.id"), nullable=False)
    send_at = Column(DateTime)
    sender_ip = Column(INET, nullable=False)
    user_agent = Column(Text)
    headers = Column(JSON, default={}, server_default="{}")
