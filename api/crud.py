# api/crud.py

from sqlalchemy.orm import Session
from . import models, security

def get_user_by_email(db: Session, email: str):
    """Fetches a single user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, password: str):
    """Creates a new user in the database."""
    hashed_password = security.get_password_hash(password)
    db_user = models.User(email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
