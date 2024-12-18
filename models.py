from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime, BLOB, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    word = Column(String, index=True, nullable=False)
    definition = Column(String, nullable=False)
    phonetic_spelling = Column(String, nullable=True)
    pronunciation_audio = Column(BLOB, nullable=True)  # Store audio as BLOB
    part_of_speech = Column(String, nullable=True)

    # Use JSON for lists
    synonyms = Column(JSON, nullable=True)
    common_collocations = Column(JSON, nullable=True)
    register = Column(String, nullable=True)
    example = Column(String, nullable=True)
    category = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # Use JSON for lists
    difficulty = Column(String, default="medium")

    @validates('synonyms', 'common_collocations', 'tags')
    def convert_list_to_json(self, key, value):
        """Ensure lists are stored as JSON strings in the database."""
        if isinstance(value, list):
            return value
        return []

    class Config:
        from_attributes = True  # This tells Pydantic to treat SQLAlchemy models as dictionaries



class UserWordProgress(Base):
    __tablename__ = 'user_word_progress'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)

    status = Column(String, nullable=False)  # not started, active, waiting, learned
    review_count = Column(Integer, default=0)  # number of times reviewed
    review_spacing = Column(Integer, default=0)  # duration to wait (in days)
    review_last_date = Column(DateTime, nullable=True)  # datetime of the last review




# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # For local development

# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create the database tables
Base.metadata.create_all(bind=engine)

# Session local to manage connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
