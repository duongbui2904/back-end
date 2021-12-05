from datetime import date
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/login")
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user is None:
        raise HTTPException(401, "Email does not exist")
    if db_user.password != user.password:
        raise HTTPException(401, "Wrong email or password")
    # resp = Response("{}", media_type="application/json")
    # resp.set_cookie("user_id", db_user.id, samesite="none", max_age=3600)
    resp = {"token": db_user.id}
    return resp


@app.post("/logout")
def logout(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user is None:
        raise HTTPException(401, "Email does not exist")
    if db_user.password != user.password:
        raise HTTPException(401, "Wrong email or password")
    resp = Response()
    resp.set_cookie("user_id", "", max_age=0)
    return resp


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/me/notes", response_model=schemas.Note)
def create_note_for_user(
    note: schemas.NoteCreate,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    user_id = int(token)
    return crud.create_user_note(db=db, note=note, user_id=user_id)


@app.get("/me/notes", response_model=List[schemas.Note])
def read_notes(
    token: str = Depends(oauth2_scheme),
    query: Optional[str] = None,
    after: Optional[date] = None,
    before: Optional[date] = None,
    tags: List[str] = Query([]),
    db: Session = Depends(get_db),
):
    user_id = int(token)
    notes = crud.get_user_notes(
        db, user_id, query=query, after=after, before=before, tags=tags
    )
    return notes


@app.get("/notes/{note_id}", response_model=schemas.Note)
def get_note(
    note_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    db_note = crud.get_note(db=db, note_id=note_id)
    if db_note is None:
        raise HTTPException(404, "Note does not exist")
    return db_note


@app.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    return crud.delete_note(db=db, note_id=note_id)
