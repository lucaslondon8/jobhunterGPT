#!/usr/bin/env python3
"""
Complete Multi-User Backend for JobHuntGPT
Integrates your existing CV analyzer, matcher, and scraper with user authentication
"""

# api/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User preferences
    target_roles = Column(JSON, default=list)  # ["developer", "engineer"]
    target_industries = Column(JSON, default=list)  # ["blockchain", "fintech"]
    location_preferences = Column(JSON, default=list)  # ["Remote", "London"]
    salary_range = Column(JSON, default=dict)  # {"min": 50000, "max": 80000}
    
    # Relationships
    cv_profiles = relationship("CVProfile", back_populates="user", cascade="all, delete-orphan")
    job_matches = relationship("JobMatch", back_populates="user", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")

class CVProfile(Base):
    __tablename__ = "cv_profiles"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # CV Analysis Results (from your cv_analyzer.py)
    experience_level = Column(String)  # junior, mid, senior, executive
    primary_industry = Column(String)  # devops_cloud, cybersecurity, etc.
    skills = Column(JSON, default=list)  # extracted skills
    skill_weights = Column(JSON, default=dict)  # skill importance weights
    user_profile_type = Column(String)  # from dynamic analysis
    confidence_score = Column(Float)
    
    # Search Strategy (from your analyzer)
    target_job_sites = Column(JSON, default=list)
    search_keywords = Column(JSON, default=list)
    salary_range = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="cv_profiles")
    job_matches = relationship("JobMatch", back_populates="cv_profile")

class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    cv_profile_id = Column(String, ForeignKey("cv_profiles.id"), nullable=False)
    
    # Job Details (from your scraper)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    salary = Column(String)
    description = Column(Text)
    tags = Column(JSON, default=list)
    source = Column(String)  # remote_ok, indeed, crypto_jobs, etc.
    job_url = Column(String)
    contact_email = Column(String)
    
    # Matching Results (from your matcher)
    match_score = Column(Float)  # 0.0 to 1.0
    score_breakdown = Column(JSON, default=dict)  # detailed scoring
    matching_keywords = Column(JSON, default=list)
    missing_keywords = Column(JSON, default=list)
    match_strength = Column(String)  # Excellent, Strong, Good, etc.
    application_priority = Column(String)  # High, Medium, Low, Skip
    
    # Status
    discovered_at = Column(DateTime, default=datetime.utcnow)
    is_relevant = Column(Boolean, default=True)
    user_rating = Column(Integer)  # 1-5 user rating
    
    # Relationships
    user = relationship("User", back_populates="job_matches")
    cv_profile = relationship("CVProfile", back_populates="job_matches")
    applications = relationship("Application", back_populates="job_match")

class Application(Base):
    __tablename__ = "applications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    job_match_id = Column(String, ForeignKey("job_matches.id"), nullable=False)
    
    # Application Details
    cover_letter = Column(Text)  # generated cover letter
    custom_message = Column(Text)  # user customization
    recipient_email = Column(String)
    subject_line = Column(String)
    
    # Status Tracking
    status = Column(String, default="pending")  # pending, sent, responded, rejected, interview
    sent_at = Column(DateTime)
    response_received_at = Column(DateTime)
    response_type = Column(String)  # positive, negative, interview_request
    
    # Email Integration
    email_message_id = Column(String)  # for tracking
    email_thread_id = Column(String)
    
    # Analytics
    open_tracking = Column(Boolean, default=False)
    click_tracking = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    job_match = relationship("JobMatch", back_populates="applications")

class UserActivity(Base):
    __tablename__ = "user_activities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    activity_type = Column(String, nullable=False)  # cv_upload, job_discovery, application_sent
    description = Column(String)
    metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# api/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from urllib.parse import quote_plus

# Database URL from environment variables
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://jobhuntgpt:your_password@localhost:5432/jobhuntgpt"
)

# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get DB session
def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# api/auth.py
from fastapi_users import FastAPIUsers, BaseUserManager
from fastapi_users.authentication import CookieAuthentication, JWTAuthentication
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends
from sqlalchemy.orm import Session
import os
import uuid

from .database import get_database_session
from .models import User

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY

    async def on_after_register(self, user: User, request = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

async def get_user_db(session: Session = Depends(get_database_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

# Authentication backends
cookie_authentication = CookieAuthentication(secret=SECRET_KEY, lifetime_seconds=3600)
jwt_authentication = JWTAuthentication(secret=SECRET_KEY, lifetime_seconds=3600)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [cookie_authentication, jwt_authentication],
)

current_active_user = fastapi_users.current_user(active=True)

# api/core.py - Integrate your existing logic
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import json

from .models import User, CVProfile, JobMatch, Application
from .database import get_database_session

# Import your existing modules
from cv_analyzer import UniversalCVAnalyzer
from match_job import RealJobMatcher, batch_match_jobs
from scraper.scrape_and_match import RealJobScraper

class JobHuntGPTCore:
    """Core business logic integrating your existing modules with database"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.cv_analyzer = UniversalCVAnalyzer()
        self.job_matcher = RealJobMatcher()
        self.job_scraper = RealJobScraper()
    
    async def analyze_user_cv(self, user_id: str, cv_text: str) -> CVProfile:
        """Analyze CV and store profile"""
        
        # Use your existing CV analyzer
        analysis = self.cv_analyzer.analyze_cv(cv_text)
        
        # Create CV profile in database
        cv_profile = CVProfile(
            user_id=user_id,
            experience_level=analysis['experience_level'],
            primary_industry=analysis['primary_industry'],
            skills=analysis['skills'],
            skill_weights=analysis['skill_weights'],
            user_profile_type=analysis['user_profile']['profile_type'],
            confidence_score=analysis['analysis_confidence'],
            target_job_sites=analysis['search_strategy']['target_job_sites'],
            search_keywords=analysis['search_strategy']['search_keywords'],
            salary_range=analysis['search_strategy']['recommended_filters']['salary_range']
        )
        
        # Deactivate old profiles
        self.db.query(CVProfile).filter(
            CVProfile.user_id == user_id,
            CVProfile.is_active == True
        ).update({CVProfile.is_active: False})
        
        self.db.add(cv_profile)
        self.db.commit()
        self.db.refresh(cv_profile)
        
        return cv_profile
    
    async def discover_jobs_for_user(self, user_id: str, max_jobs: int = 50) -> List[JobMatch]:
        """Discover and match jobs for user"""
        
        # Get active CV profile
        cv_profile = self.db.query(CVProfile).filter(
            CVProfile.user_id == user_id,
            CVProfile.is_active == True
        ).first()
        
        if not cv_profile:
            raise ValueError("No active CV profile found")
        
        # Use your existing scraper
        target_sites = cv_profile.target_job_sites
        search_keywords = cv_profile.search_keywords
        
        scraped_jobs = []
        
        # Scrape from different sources based on profile
        if 'remote_ok' in target_sites:
            scraped_jobs.extend(self.job_scraper.scrape_remote_ok(search_keywords, limit=15))
        
        if 'indeed' in target_sites:
            scraped_jobs.extend(self.job_scraper.scrape_indeed_uk(search_keywords, limit=15))
        
        if 'crypto_jobs' in target_sites:
            scraped_jobs.extend(self.job_scraper.scrape_crypto_jobs(limit=10))
        
        # Match jobs using your existing matcher
        cv_text = f"Skills: {', '.join(cv_profile.skills)} Experience: {cv_profile.experience_level} Industry: {cv_profile.primary_industry}"
        
        job_matches = []
        for job_data in scraped_jobs[:max_jobs]:
            
            # Calculate match score using your matcher
            job_text = f"{job_data.get('title', '')} {job_data.get('description', '')} {job_data.get('company', '')}"
            match_analysis = self.job_matcher.analyze_match(cv_text, job_text)
            
            # Create job match record
            job_match = JobMatch(
                user_id=user_id,
                cv_profile_id=cv_profile.id,
                title=job_data.get('title', ''),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                salary=job_data.get('salary', ''),
                description=job_data.get('description', ''),
                tags=job_data.get('tags', []),
                source=job_data.get('source', ''),
                job_url=job_data.get('url', ''),
                contact_email=job_data.get('contact_email', ''),
                match_score=match_analysis['overall_score'],
                score_breakdown=match_analysis['score_breakdown'],
                matching_keywords=match_analysis['matching_keywords'],
                missing_keywords=match_analysis['missing_keywords'],
                match_strength=match_analysis['match_strength'],
                application_priority=match_analysis['application_priority']
            )
            
            self.db.add(job_match)
            job_matches.append(job_match)
        
        self.db.commit()
        return job_matches
    
    async def create_application(self, user_id: str, job_match_id: str, 
                               custom_message: str = None) -> Application:
        """Create job application with generated cover letter"""
        
        job_match = self.db.query(JobMatch).filter(JobMatch.id == job_match_id).first()
        if not job_match:
            raise ValueError("Job match not found")
        
        # Generate cover letter using your existing logic
        from generate_cover_letter import generate_cover_letter_for_job
        
        cover_letter = generate_cover_letter_for_job(
            job_title=job_match.title,
            company=job_match.company,
            job_description=job_match.description,
            user_profile=job_match.cv_profile
        )
        
        # Create application
        application = Application(
            user_id=user_id,
            job_match_id=job_match_id,
            cover_letter=cover_letter,
            custom_message=custom_message,
            recipient_email=job_match.contact_email,
            subject_line=f"Application for {job_match.title} at {job_match.company}"
        )
        
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        
        return application

# Updated main.py to include authentication and database
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from .auth import fastapi_users, current_active_user, jwt_authentication
from .models import User, CVProfile, JobMatch, Application, Base
from .database import engine, get_database_session
from .core import JobHuntGPTCore

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JobHuntGPT Multi-User API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
app.include_router(
    fastapi_users.get_auth_router(jwt_authentication),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(),
    prefix="/users",
    tags=["users"],
)

# Protected endpoints
@app.post("/api/upload-cv")
async def upload_cv(
    file: UploadFile = File(...),
    user: User = Depends(current_active_user),
    db: Session = Depends(get_database_session)
):
    """Upload and analyze CV for authenticated user"""
    
    # Read file content
    content = await file.read()
    cv_text = content.decode('utf-8')
    
    # Use core logic
    core = JobHuntGPTCore(db)
    cv_profile = await core.analyze_user_cv(user.id, cv_text)
    
    return {
        "success": True,
        "profile_id": cv_profile.id,
        "analysis": {
            "experience_level": cv_profile.experience_level,
            "primary_industry": cv_profile.primary_industry,
            "skills_count": len(cv_profile.skills),
            "confidence": cv_profile.confidence_score
        }
    }

@app.post("/api/discover-jobs")
async def discover_jobs(
    max_jobs: int = 50,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_database_session)
):
    """Discover jobs for authenticated user"""
    
    core = JobHuntGPTCore(db)
    job_matches = await core.discover_jobs_for_user(user.id, max_jobs)
    
    return {
        "success": True,
        "jobs_found": len(job_matches),
        "top_matches": [
            {
                "id": job.id,
                "title": job.title,
                "company": job.company,
                "match_score": job.match_score,
                "priority": job.application_priority
            }
            for job in sorted(job_matches, key=lambda x: x.match_score, reverse=True)[:10]
        ]
    }

@app.get("/api/my-jobs")
async def get_my_jobs(
    user: User = Depends(current_active_user),
    db: Session = Depends(get_database_session)
):
    """Get user's job matches"""
    
    jobs = db.query(JobMatch).filter(
        JobMatch.user_id == user.id,
        JobMatch.is_relevant == True
    ).order_by(JobMatch.match_score.desc()).limit(20).all()
    
    return [
        {
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "salary": job.salary,
            "match_score": round(job.match_score * 100, 1),
            "match_strength": job.match_strength,
            "priority": job.application_priority,
            "contact_email": job.contact_email,
            "source": job.source
        }
        for job in jobs
    ]

@app.post("/api/apply-job/{job_id}")
async def apply_to_job(
    job_id: str,
    custom_message: str = None,
    user: User = Depends(current_active_user),
    db: Session = Depends(get_database_session)
):
    """Apply to a job"""
    
    core = JobHuntGPTCore(db)
    application = await core.create_application(user.id, job_id, custom_message)
    
    return {
        "success": True,
        "application_id": application.id,
        "cover_letter_preview": application.cover_letter[:200] + "..."
    }

@app.get("/api/my-applications")
async def get_my_applications(
    user: User = Depends(current_active_user),
    db: Session = Depends(get_database_session)
):
    """Get user's applications"""
    
    applications = db.query(Application).filter(
        Application.user_id == user.id
    ).order_by(Application.created_at.desc()).all()
    
    return [
        {
            "id": app.id,
            "job_title": app.job_match.title,
            "company": app.job_match.company,
            "status": app.status,
            "applied_at": app.created_at.isoformat(),
            "response_received": app.response_received_at is not None
        }
        for app in applications
    ]

@app.get("/api/dashboard-stats")
async def get_dashboard_stats(
    user: User = Depends(current_active_user),
    db: Session = Depends(get_database_session)
):
    """Get user's dashboard statistics"""
    
    # Count user's applications
    total_applications = db.query(Application).filter(Application.user_id == user.id).count()
    
    # Count responses
    responses = db.query(Application).filter(
        Application.user_id == user.id,
        Application.response_received_at.isnot(None)
    ).count()
    
    response_rate = (responses / total_applications * 100) if total_applications > 0 else 0
    
    # Count job matches
    job_matches = db.query(JobMatch).filter(JobMatch.user_id == user.id).count()
    
    return {
        "applications_sent": total_applications,
        "response_rate": round(response_rate, 1),
        "jobs_discovered": job_matches,
        "email_discovery_rate": 100.0,  # Your proven rate
        "time_saved": total_applications * 2  # Estimate 2h per application
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
