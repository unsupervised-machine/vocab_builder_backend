from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)


class Word(Base):
    __tablename__ = 'words'

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    definition = Column(String)
    example = Column(String)
    category = Column(String)
    difficulty = Column(String)



class UserWordProgress(Base):
    __tablename__ = 'user_word_progress'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    word_id = Column(Integer, ForeignKey('words.id'), nullable=False)

    status = Column(String) # not started, active, waiting, learned
    review_count = Column(Integer) # number of times have reviewed word
    review_spacing = Column(Integer) # duration to wait until move from waiting to active
    review_last_date = Column(Integer) # date last time reviewed




# SQLite database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # For local development

# Create database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create the database tables
Base.metadata.create_all(bind=engine)

# Session local to manage connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
