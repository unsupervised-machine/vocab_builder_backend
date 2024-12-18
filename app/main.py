import bcrypt
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import crud

import schemas
from models import User, Word
from database import get_db
from schemas import UserCreate, WordCreate


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/users/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")


    hashed_password = hash_password(user.password)

    db_user = User(name=user.name, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()


@app.post("/words/")
def create_word(word: WordCreate, db: Session = Depends(get_db)):
    # db_word = db.query(Word).filter(Word.word == word.word).first()
    # if db_word:
    #     raise HTTPException(status_code=400, detail="Word already exists")

    db_word = Word(word=word.word, definition=word.definition, example=word.example, category=word.category, difficulty=word.difficulty)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

@app.get("/words/")
def read_words(db: Session = Depends(get_db)):
    words = db.query(Word).all()
    return words
