from xmlrpc.client import DateTime

from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime


# Create schema for base models
class UserBase(BaseModel):
    name: str
    email: str
    points: Optional[int] = 0

    class Config:
        from_attributes = True  # This tells Pydantic to treat SQLAlchemy models as dictionaries


class WordBase(BaseModel):
    word: str
    definition: str
    phonetic_spelling: Optional[str] = None
    audio_url: Optional[str] = None  # Store URL to the audio file
    image_url: Optional[str] = None # Store URL to the image
    part_of_speech: Optional[str] = None
    synonyms: Optional[List[str]] = None
    common_collocations: Optional[List[str]] = None  # Phrases the word is commonly used with (e.g., "serendipitous discovery").
    usage_context: Optional[str] = None  # Formality or context(e.g., formal, informal, technical).
    example: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    difficulty: Optional[str] = "medium"  # Default difficulty to "medium"

    class Config:
        from_attributes = True


class UserWordProgressBase(BaseModel):
    user_id: int
    word_id: int
    status: Literal['not started', 'active', 'waiting', 'learned']
    review_count: int
    review_spacing: int  # Duration until moving from waiting to active
    review_last_date: Optional[datetime]  # The last review date (could use int for UNIX timestamp or datetime)

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    # user_id: int
    word_list: List[int]  # list of word_ids used in the quiz

    # correct_words: List[int]  # list of word_ids scored correct in the quiz
    # incorrect_words: List[int]  # list of word_ids scored incorrect in the quiz
    # score_raw: int
    # score_percent: float

    # quiz_date: datetime
    tags: Optional[List[str]]

    class Config:
        from_attributes = True

class UserQuizBase(BaseModel):
    user_id: int
    quiz_id: int
    word_list: List[int]
    correct_words: List[int]  # list of word_ids scored correct in the quiz
    incorrect_words: List[int]  # list of word_ids scored incorrect in the quiz
    score_raw: int
    score_percent: float
    tags: Optional[List[str]]
    quiz_date: datetime


# Create schemas for POST requests (for creating new entries)

class UserCreate(UserBase):
    password: str  # Include password field for user creation


class WordCreate(WordBase):
    pass  # can add more fields later


class UserWordProgressCreate(UserWordProgressBase):
    pass  # can add more fields later


class QuizCreate(QuizBase):
    pass # can add more fields later

class UserQuizCreate(UserQuizBase):
    pass
