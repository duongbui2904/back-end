from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from . import models, schemas


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_notes(
    db: Session,
    user_id: int,
    query: Optional[str] = None,
    after: Optional[date] = None,
    before: Optional[date] = None,
    tags: List[str] = [],
) -> List[models.Note]:
    db_query = db.query(models.Note).filter_by(user_id=user_id)
    if query is not None:
        db_query = db_query.filter(
            models.Note.title.like(f"%{query}%") | models.Note.body.like(f"%{query}%")
        )
    if after is not None:
        db_query = db_query.filter(func.date(models.Note.timestamp) >= after)
    if before is not None:
        db_query = db_query.filter(func.date(models.Note.timestamp) <= before)
    if len(tags) > 0:
        db_query = db_query.filter(
            models.Note.tagged_notes.any(models.TaggedNote.tag.in_(tags))
        )
    return db_query.order_by(models.Note.timestamp.desc()).all()


def create_user_note(
    db: Session, note: schemas.NoteCreate, user_id: int
) -> models.Note:
    db_note = models.Note(title=note.title, body=note.body, user_id=user_id)
    db.add(db_note)
    db.commit()
    db_tagged_notes = [
        models.TaggedNote(tag=tag, note_id=db_note.id) for tag in note.tags
    ]
    db.bulk_save_objects(db_tagged_notes)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_note(db: Session, note_id: int) -> Optional[models.Note]:
    return db.query(models.Note).get(note_id)


def delete_note(db: Session, note_id: int) -> None:
    db.query(models.Note).filter_by(id=note_id).delete()
    db.commit()
