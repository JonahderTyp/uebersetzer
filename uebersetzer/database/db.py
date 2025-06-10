from __future__ import annotations

import logging
import re
from datetime import datetime as Datetime
from typing import List, Type, TypeVar

from flask import current_app
# from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.expression import and_
from werkzeug.security import check_password_hash, generate_password_hash


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[Datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=Datetime.now)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    language: Mapped[str] = mapped_column(String(10), nullable=False)
    translate: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)

    @staticmethod
    def create_new(
            content: str, timestamp: Datetime, author: str, language: str,
            translate: bool = True) -> Message:

        print("\n\n")
        print(timestamp)
        print(type(timestamp))
        print("\n\n")
        """Create a new message."""
        message = Message(
            content=content,
            timestamp=timestamp,
            author=author,
            language=language,
            translate=translate
        )
        db.session.add(message)
        db.session.commit()
        return message

    @staticmethod
    def get_via_id(id: int) -> Message | None:
        msg: Message = db.session.query(Message).filter_by(id=id).first()
        return msg

    @staticmethod
    def get_all_messages() -> List[Message]:
        """Get all messages."""
        return db.session.query(Message).all()

    def to_dict(self) -> dict:
        """Convert the message to a dictionary."""
        return {
            'id': self.id,
            'content': self.content,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.author,
            'language': self.language,
            'translate': self.translate
        }

    def delete(self) -> None:
        """Delete the message."""
        db.session.delete(self)
        db.session.commit()
