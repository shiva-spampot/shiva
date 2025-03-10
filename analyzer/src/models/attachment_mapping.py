from sqlalchemy import Column, BIGINT, ForeignKey, UniqueConstraint
from models.base import Base, CRUDBase, TimeStampedMixin


class AttachmentMapping(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "attachment_mapping"

    id = Column(BIGINT, primary_key=True, index=True)
    email_id = Column(BIGINT, ForeignKey("emails.id"), nullable=False)
    attachment_id = Column(
        BIGINT, ForeignKey("attachments.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("email_id", "attachment_id", name="uix_email_attachment"),
    )
