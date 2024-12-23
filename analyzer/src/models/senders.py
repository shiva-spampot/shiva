from sqlalchemy import Column, BIGINT, String
from models.base import Base, CRUDBase, TimeStampedMixin


class Senders(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "senders"

    id = Column(BIGINT, primary_key=True, index=True)
    email = Column(
        String, index=True, unique=True, comment="Sender's full email address"
    )
    domain = Column(String, comment="Domain of the Sender's email")
