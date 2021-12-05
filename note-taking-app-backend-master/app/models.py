from typing import List

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    notes: List["Note"] = relationship("Note", back_populates="user")


class Note(Base):
    __tablename__ = "note"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    body = Column(String)
    timestamp = Column(
        DateTime, index=True, server_default=func.now(), onupdate=func.now()
    )
    # tags = relationship("Tag", back_populates="user")
    user_id = Column(Integer, ForeignKey("user.id"))
    user: User = relationship(User, back_populates="notes")
    tagged_notes: List["TaggedNote"] = relationship(
        "TaggedNote", uselist=True, back_populates="note"
    )

    @property
    def tags(self) -> List[str]:
        return [tag.tag for tag in self.tagged_notes]


class TaggedNote(Base):
    __tablename__ = "tagged_note"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, nullable=False)
    note_id = Column(Integer, ForeignKey("note.id"))
    note = relationship(Note, uselist=False)
