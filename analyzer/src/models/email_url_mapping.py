from sqlalchemy import Column, BIGINT, ForeignKey, UniqueConstraint
from models.base import Base, CRUDBase, TimeStampedMixin


class EmailURLMapping(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "email_url_mapping"

    id = Column(BIGINT, primary_key=True, index=True)
    email_id = Column(BIGINT, ForeignKey("emails.id"), nullable=False)
    url_id = Column(BIGINT, ForeignKey("email_urls.id"), nullable=False)

    __table_args__ = (UniqueConstraint("email_id", "url_id", name="uix_email_url"),)
