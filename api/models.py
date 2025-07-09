import uuid
from datetime import datetime
from sqlalchemy import (Column, Integer, String, Text, DateTime, Float, 
                        Boolean, ForeignKey, JSON)
from sqlalchemy.orm import relationship, declarative_base

# A single Base for all models to inherit from
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    cv_profiles = relationship("CVProfile", back_populates="user", cascade="all, delete-orphan")
    job_matches = relationship("JobMatch", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")

class CVProfile(Base):
    __tablename__ = "cv_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    experience_level = Column(String)
    primary_industry = Column(String)
    skills = Column(JSON, default=list)
    search_keywords = Column(JSON, default=list)
    full_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="cv_profiles")
    job_matches = relationship("JobMatch", back_populates="cv_profile")

class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    cv_profile_id = Column(String, ForeignKey("cv_profiles.id"), nullable=False)
    
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    salary = Column(String)
    description = Column(Text)
    source = Column(String)
    job_url = Column(String, unique=True)
    contact_email = Column(String)
    
    match_score = Column(Float)
    score_breakdown = Column(JSON, default=dict)
    match_strength = Column(String)
    application_priority = Column(String)
    
    discovered_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="job_matches")
    cv_profile = relationship("CVProfile", back_populates="job_matches")
    application = relationship("Application", back_populates="job_match", uselist=False)

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_match_id = Column(String, ForeignKey("job_matches.id"), unique=True, nullable=False)
    
    status = Column(String, default="applied")
    sent_at = Column(DateTime, default=datetime.utcnow)
    
    # --- ADDED: Fields to log the application details ---
    recipient_email = Column(String)
    cover_letter_text = Column(Text)
    # ----------------------------------------------------
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="applications")
    job_match = relationship("JobMatch", back_populates="application")

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    activity_type = Column(String, nullable=False)
    description = Column(String)
    activity_metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)
