import bcrypt
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import crud
from fastapi.middleware.cors import CORSMiddleware

import logging

import schemas
from models import User, Word, UserWordProgress, Quiz, UserQuiz
from database import get_db
from schemas import UserCreate, WordCreate, UserWordProgressCreate, QuizCreate, UserQuizCreate, UserUpdate, LoginRequest


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def verify_password(input_password: str, hashed_password: str) -> bool:
    input_password_bytes = input_password.encode('utf-8')
    return bcrypt.checkpw(input_password_bytes, hashed_password.encode('utf-8'))

app = FastAPI()

# Enable CORS for all origins (not recommended for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (can be restricted based on requirement)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-Custom-Header", "Content-Type"],
)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.post("/login/")
async def login(login_credentials: LoginRequest, db: Session = Depends(get_db)):
    # Log received email and password
    print(f"Received email: {login_credentials.email}, password: {login_credentials.password}")

    db_user = (db.query(User)
        .filter(
    User.email == login_credentials.email,
        )
        .first()
        )
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(login_credentials.password, db_user.password):
        print("Invalid password")
        raise HTTPException(status_code=401, detail="Invalid password")

    # Successfully authenticated, return user ID
    return {"id": db_user.id}


@app.post("/users/register")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    db_user = User(name=user.name, email=user.email, password=hashed_password, points=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/users/{user_id}/update")
async def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if email is being updated and ensure it's unique
    if user_update.email and user_update.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Update the fields that are provided
    if user_update.name is not None:
        db_user.name = user_update.name
    if user_update.email is not None:
        db_user.email = user_update.email
    if user_update.password is not None:
        db_user.password = hash_password(user_update.password)

    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users/")
async def read_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@app.get("/users/by-id/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    return db.query(User).filter(User.id == user_id).first()

@app.get("/users/by-email/{email}")
async def get_user(email: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first()


@app.post("/words/")
async def create_word(word: WordCreate, db: Session = Depends(get_db)):
    db_word = db.query(Word).filter(Word.word == word.word).first()
    if db_word:
        raise HTTPException(status_code=400, detail="Word already exists")

    # db_word = Word(word=word.word, definition=word.definition, example=word.example, category=word.category, difficulty=word.difficulty)
    db_word = Word(
        word=word.word,
        definition=word.definition,
        phonetic_spelling=word.phonetic_spelling,
        audio_url=word.audio_url,
        image_url=word.image_url,
        part_of_speech=word.part_of_speech,
        synonyms=word.synonyms,  # These will be automatically serialized as JSON if needed
        common_collocations=word.common_collocations,
        usage_context=word.usage_context,
        example=word.example,
        category=word.category,
        tags=word.tags,  # These will be serialized if needed
        difficulty=word.difficulty
    )

    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

@app.get("/words/")
async def read_words(db: Session = Depends(get_db)):
    words = db.query(Word).all()
    return words

@app.get("/words/{word_id}")
async def get_word(word_id: int, db: Session = Depends(get_db)):
    word = db.query(Word).filter(Word.id == word_id).first()
    return word


@app.post("/users/{user_id}/user_word_progress/{word_id}")
async def upsert_user_word_progress(
        user_id: int,
        word_id: int,
        usr_wrd_prog: UserWordProgressCreate,
        db: Session = Depends(get_db)
):
    # Log the input data
    logging.info(f"Received data: {usr_wrd_prog}")
    logging.info(f"user_id: {user_id}, word_id: {word_id}")

    # If an ID is provided, try to fetch the existing record
    if usr_wrd_prog.id:
        existing_progress = (
            db.query(UserWordProgress)
            .filter(
                UserWordProgress.id == usr_wrd_prog.id,
                UserWordProgress.user_id == usr_wrd_prog.user_id,
                UserWordProgress.word_id == usr_wrd_prog.word_id,
            )
            .first()
        )

        if existing_progress:
            # Update the existing record if it matches the provided user_id and word_id
            existing_progress.status = usr_wrd_prog.status
            existing_progress.review_count = usr_wrd_prog.review_count
            existing_progress.review_spacing = usr_wrd_prog.review_spacing
            existing_progress.review_last_date = usr_wrd_prog.review_last_date
            db.commit()
            db.refresh(existing_progress)
            return {"message": "Progress updated", "data": existing_progress}

    # Check if user exists
    user_exists = db.query(User).filter(User.id == user_id).first()
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if word exists
    word_exists = db.query(Word).filter(Word.id == word_id).first()
    if not word_exists:
        raise HTTPException(status_code=404, detail="Word not found")

    # If no existing record is found, create a new one
    new_progress = UserWordProgress(
        user_id=usr_wrd_prog.user_id,
        word_id=usr_wrd_prog.word_id,
        status=usr_wrd_prog.status,
        review_count=usr_wrd_prog.review_count,
        review_spacing=usr_wrd_prog.review_spacing,
        review_last_date=usr_wrd_prog.review_last_date,
    )
    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)
    return {"message": "Progress created", "data": new_progress}

@app.get("/users/{user_id}/user_word_progress/")
async def read_user_word_progress(user_id: int, db: Session = Depends(get_db)):
    user_word_progress = db.query(UserWordProgress).filter(UserWordProgress.user_id == user_id).all()
    return user_word_progress

@app.get("/users/{user_id}/user_word_progress/{word_id}")
async def get_user_word_progress(user_id: int, word_id: int, db: Session = Depends(get_db)):
    return (
        db.query(UserWordProgress)
        .filter(
            UserWordProgress.user_id == user_id,
            UserWordProgress.word_id == word_id
        )
        .first()
    )


@app.post("/quizzes/")
async def create_quiz_template(quiz_tmplt: QuizCreate, db: Session = Depends(get_db)):
    db_quiz = Quiz(
        word_list=quiz_tmplt.word_list,
        tags=quiz_tmplt.tags,
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return {"message": "Quiz template created", "data": db_quiz}

@app.get("/quizzes/")
async def read_quiz(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).all()
    return quizzes

@app.get("/quizzes/{quiz_id}")
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    return quiz


@app.post("/users/{user_id}/user_quizzes/")
async def create_user_quiz(user_id: int, usr_quiz: UserQuizCreate, db: Session = Depends(get_db)):
    if user_id != usr_quiz.user_id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    new_usr_quiz = UserQuiz(
        user_id=usr_quiz.user_id,
        quiz_id=usr_quiz.quiz_id,
        correct_words=usr_quiz.correct_words,
        incorrect_words=usr_quiz.incorrect_words,
        score_raw=usr_quiz.score_raw,
        score_percent=usr_quiz.score_percent,
        quiz_date=usr_quiz.quiz_date,
    )
    db.add(new_usr_quiz)
    db.commit()
    db.refresh(new_usr_quiz)
    return {"message": "User quiz created", "data": new_usr_quiz}

@app.get("/users/{user_id}/user_quizzes/")
async def read_user_quiz(user_id: int, db: Session = Depends(get_db)):
    user_quiz = db.query(UserQuiz).filter(UserQuiz.user_id == user_id).all()
    return user_quiz

@app.get("/users/{user_id}/user_quizzes/{user_quiz_id}")
async def read_user_quiz(user_id: int, user_quiz_id: int, db: Session = Depends(get_db)):
        result = (db.query(UserQuiz)
        .filter(
            UserQuiz.user_id == user_id,
            UserQuiz.id == user_quiz_id,
        )
        .first()
        )
        if not result:
            raise HTTPException(status_code=404, detail="User quiz not found")

        return result