# api/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the entry point to the database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # This argument IS REQUIRED for SQLite
    connect_args={"check_same_thread": False} 
)

# A session is the handle for all conversations with the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
