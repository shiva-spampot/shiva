from sqlalchemy import Column, BIGINT, Text, Boolean, CHAR
from models.base import Base, CRUDBase, TimeStampedMixin


class URLs(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "urls"

    id = Column(BIGINT, primary_key=True, index=True)
    url = Column(Text, nullable=False, comment="The full URL extracted from the email")
    domain = Column(Text, nullable=False, comment="Extracted domain from the URL")
    is_malicious = Column(Boolean, default=False, server_default="false")
    url_sha256 = Column(
        CHAR(64),
        nullable=False,
        comment="Hash of the URL (SHA256) for fast comparisons",
    )
