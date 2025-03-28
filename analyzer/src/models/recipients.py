from sqlalchemy import Column, BIGINT, String
from models.base import Base, CRUDBase, TimeStampedMixin


class Recipients(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "recipients"

    id = Column(BIGINT, primary_key=True, index=True)
    email = Column(
        String,
        index=True,
        unique=True,
        nullable=False,
        comment="Recipient's full email address",
    )
    domain = Column(String, nullable=False, comment="Domain of the recipient's email")
