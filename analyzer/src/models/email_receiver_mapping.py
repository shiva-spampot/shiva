from sqlalchemy import Column, BIGINT, ForeignKey, Integer, UniqueConstraint
from models.base import Base, CRUDBase, TimeStampedMixin


class EmailReceiverMapping(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "email_receiver_mapping"

    id = Column(BIGINT, primary_key=True, index=True)
    email_id = Column(BIGINT, ForeignKey("emails.id"), nullable=False)
    receiver_id = Column(BIGINT, ForeignKey("receivers.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("email_id", "receiver_id", name="uix_email_receiver"),
    )
