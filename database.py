from sqlalchemy.orm import Session
from models import SessionLocal

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
