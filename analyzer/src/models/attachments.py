from sqlalchemy import Column, BIGINT, ForeignKey, String, CHAR
from models.base import Base, CRUDBase, TimeStampedMixin


class Attachments(Base, CRUDBase, TimeStampedMixin):
    __tablename__ = "attachments"

    id = Column(BIGINT, primary_key=True, index=True)
    file_name = Column(String, nullable=False, comment="File name")
    file_size = Column(BIGINT, nullable=False, comment="File size in bytes")
    file_type = Column(
        String,
        nullable=False,
        comment="MIME type of the file (e.g., image/jpeg, application/pdf)",
    )
    attachment_file_url = Column(
        String, nullable=False, comment="Path/URL to the external storage"
    )
    file_extension = Column(
        String, comment="File extension (e.g., .jpg, .pdf, .exe)"
    )
    file_sha256 = Column(
        CHAR(64),
        nullable=False,
        comment="Hash of the file (SHA256) for file identification",
    )
