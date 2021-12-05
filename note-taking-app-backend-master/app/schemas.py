from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class NoteBase(BaseModel):
    title: str
    body: str
    tags: List[str] = []


class NoteCreate(NoteBase):
    pass


class Note(NoteBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):

    email: str


class UserCreate(UserBase):

    password: str


class User(UserBase):
    id: int
    # items: List[Note] = []

    class Config:
        orm_mode = True
