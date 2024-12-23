from typing import Union
from sqlalchemy import Column, DateTime, Select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import validates
from sqlalchemy.event import listen
from helpers.common import get_utc_datetime
from sqlalchemy.orm import Session


Base = declarative_base()


class CRUDBase:
    """Base class with common CRUD methods for SQLAlchemy models."""

    @classmethod
    def get_all(cls, db_session: Session, query: Union[dict, Select] = {}):
        select_query = db_session.query(cls)

        if query:
            if isinstance(query, dict):
                select_query = select_query.filter_by(**query)
            else:
                select_query = query

        return select_query.all()

    @classmethod
    def get_by_id(cls, db_session: Session, item_id):
        return db_session.query(cls).filter(cls.id == item_id).first()

    @classmethod
    def create(cls, db_session: Session, **kwargs):
        new_instance = cls(**kwargs)
        db_session.add(new_instance)
        db_session.commit()
        db_session.refresh(new_instance)
        return new_instance

    @classmethod
    def update(cls, db_session: Session, item_id, **kwargs):
        instance = db_session.query(cls).filter(cls.id == item_id).first()
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db_session.commit()
            db_session.refresh(instance)
            return instance
        return None

    @classmethod
    def delete_by_id(cls, db_session: Session, item_id):
        instance = db_session.query(cls).filter(cls.id == item_id).first()
        if instance:
            db_session.delete(instance)
            db_session.commit()
            return True
        return False


class TimeStampedMixin:
    """Mixin class for adding created_at and modified_at fields."""

    created_at = Column(DateTime, default=get_utc_datetime, server_default=func.now())
    modified_at = Column(
        DateTime,
        default=get_utc_datetime,
        onupdate=get_utc_datetime,
        server_default=func.now(),
    )

    @validates("created_at")
    def validate_created_at(self, key, value):
        return value or get_utc_datetime()

    @validates("modified_at")
    def validate_modified_at(self, key, value):
        return value or get_utc_datetime()

    # Listen for updates and automatically update the modified_at field
    @staticmethod
    def _on_update(mapper, connection, target):
        target.modified_at = get_utc_datetime()


# Register the event listener to automatically update `modified_at`
listen(Base, "before_update", TimeStampedMixin._on_update)
