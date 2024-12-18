from xmlrpc.client import DateTime

from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime


# Create schema for base models (should not be directly used maybe?)
class UserBase(BaseModel):
    # id: int -- DONT NEED AUTO GENERATED by SQLALCHEMY
    name: str
    email: str

    class Config:
        from_attributes = True  # This tells Pydantic to treat SQLAlchemy models as dictionaries


class WordBase(BaseModel):
    # id: int -- DONT NEED AUTO GENERATED by SQLALCHEMY
    word: str
    definition: str
    phonetic_spelling: Optional[str] = None
    pronunciation_audio: Optional[bytes] = None  # Store audio as binary data
    part_of_speech: Optional[str] = None
    synonyms: Optional[List[str]] = None
    common_collocations: Optional[List[str]] = None  # Phrases the word is commonly used with (e.g., "serendipitous discovery").
    register: Optional[str] = None  # Formality or context(e.g., formal, informal, technical).
    example: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: Optional[str] = "medium"  # Default difficulty to "medium"

    class Config:
        from_attributes = True



class UserWordProgressBase(BaseModel):
    # id: int -- DONT NEED AUTO GENERATED by SQLALCHEMY
    user_id: int
    word_id: int
    # status: str  # not started, active, waiting, learned
    status: Literal['not started', 'active', 'waiting', 'learned']
    review_count: int
    review_spacing: int  # Duration until moving from waiting to active
    review_last_date: Optional[datetime]  # The last review date (could use int for UNIX timestamp or datetime)

    class Config:
        from_attributes = True




# Create schemas for POST requests (for creating new entries)

class UserCreate(UserBase):
    password: str  # Include password field for user creation


class WordCreate(WordBase):
    pass  # can add more fields later


class UserWordProgressCreate(UserWordProgressBase):
    pass  # can add more fields later



# Read schemas for GET responses

class User(UserBase):
    word_progresses: List[UserWordProgressBase] = []  # Include the user's progress

    class Config:
        from_attributes = True


class Word(WordBase):
    user_progresses: List[UserWordProgressBase] = []  # Include the users' progress on this word

    class Config:
        from_attributes = True


class UserWordProgress(UserWordProgressBase):
    user: UserBase  # Include user details in the progress response
    word: WordBase  # Include word details in the progress response

    class Config:
        from_attributes = True