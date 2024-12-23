from sqlalchemy import Column, BIGINT, Text
from models.base import Base, CRUDBase, TimeStampedMixin


class RawEmails(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "raw_emails"

    id = Column(BIGINT, primary_key=True, index=True)
    data = Column(Text, nullable=False)
