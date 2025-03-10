from sqlalchemy import Column, BIGINT, ForeignKey, Integer, UniqueConstraint
from models.base import Base, CRUDBase, TimeStampedMixin


class RecipientsMapping(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "recipients_mapping"

    id = Column(BIGINT, primary_key=True, index=True)
    email_id = Column(BIGINT, ForeignKey("emails.id"), nullable=False)
    recipient_id = Column(BIGINT, ForeignKey("recipients.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("email_id", "recipient_id", name="uix_email_recipient"),
    )
