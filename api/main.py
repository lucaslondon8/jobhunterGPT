#!/usr/bin/env python3
"""
JobHuntGPT API - Main Controller
Orchestrates CV analysis, job scraping, and intelligent matching.
"""

import os
import sys
import io
import traceback
import cohere
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

# Load environment variables from .env file
load_dotenv()

# NOTE: The following two lines for modifying sys.path are no longer needed
# when you install the project as a package (with `pip install .`) but are
# left here for reference. They don't harm anything if left in.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# --- CORRECTED Module Imports ---
# Use relative imports for a packaged application
from ..analyzer.cv_analyzer import analyze_cv_for_search
from ..matcher.match_job import batch_match_jobs
from ..scraper.dynamic_scraper import DynamicJobScraper
from . import models, schemas, crud, security
from .database import engine, get_db

# --- Document Processing Imports ---
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Create database tables based on the models
models.Base.metadata.create_all(bind=engine)

# --- Initialize Cohere Client ---
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    print("⚠️ Warning: COHERE_API_KEY not found in .env file. Cover letter generation will fail.")
co = cohere.Client(cohere_api_key)
# ------------------------------------


# --- FastAPI App Initialization ---
app = FastAPI(
    title="JobHuntGPT API",
    version="5.0.2",
    description="Multi-user API with JWT authentication and AI cover letter generation."
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Dependency for getting the current user ---
async def get_current_active_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Dependency to get the current user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except security.JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=email)
    if user is None or not user.is_active:
        raise credentials_exception
    return user

# --- Helper Functions for text extraction ---
def extract_text_from_pdf(content: bytes) -> str:
    if not PDF_AVAILABLE: raise HTTPException(status_code=501, detail="PDF library not installed.")
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process PDF file: {e}")

def extract_text_from_docx(content: bytes) -> str:
    if not DOCX_AVAILABLE: raise HTTPException(status_code=501, detail="DOCX library not installed.")
    try:
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process DOCX file: {e}")

# --- API Endpoints ---
@app.get("/")
async def root():
    return {"message": "JobHuntGPT API is running. Navigate to /docs for API documentation."}

# --- Authentication endpoints ---
@app.post("/api/users/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, email=user.email, password=user.password)

@app.post("/api/auth/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    return current_user


# --- CV upload endpoint ---
@app.post("/api/upload-cv", response_model=schemas.CVAnalysisResponse)
async def upload_cv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Handles CV upload, analysis, saves full text, and clears old job matches."""
    content = await file.read()
    filename = file.filename.lower()
    cv_text = ""

    try:
        if filename.endswith('.pdf'):
            cv_text = extract_text_from_pdf(content)
        elif filename.endswith('.docx'):
            cv_text = extract_text_from_docx(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please use PDF, DOCX.")

        analysis = analyze_cv_for_search(cv_text)
        db.query(models.JobMatch).filter(models.JobMatch.user_id == current_user.id).delete()

        cv_profile = models.CVProfile(
            user_id=current_user.id,
            experience_level=analysis.get('experience_level'),
            primary_industry=analysis.get('industry_category'),
            skills=analysis.get('skills'),
            search_keywords=analysis.get('search_keywords'),
            full_text=cv_text
        )
        db.add(cv_profile)
        db.commit()

        return schemas.CVAnalysisResponse(success=True, analysis=analysis, message="CV analyzed and profile saved.")
    except Exception as e:
        db.rollback()
        print(f"❌ CV upload error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# --- Job discovery endpoint ---
@app.post("/api/discover-jobs")
async def discover_jobs(max_jobs: int = 50, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """Discovers jobs based on the user's latest CV and saves unique matches."""
    latest_cv = db.query(models.CVProfile).filter(models.CVProfile.user_id == current_user.id).order_by(models.CVProfile.created_at.desc()).first()
    if not latest_cv:
        raise HTTPException(status_code=400, detail="A CV must be uploaded before discovering jobs.")
    try:
        keywords = latest_cv.search_keywords
        existing_urls = {job.job_url for job in db.query(models.JobMatch.job_url).filter(models.JobMatch.user_id == current_user.id).all()}
        scraper = DynamicJobScraper()
        scraped_jobs = await scraper.scrape_jobs_with_keywords(keywords, max_jobs=max_jobs)
        new_jobs_added = 0
        if scraped_jobs:
            for job_data in scraped_jobs:
                job_url = job_data.get('url')
                if job_url and job_url not in existing_urls:
                    job_match = models.JobMatch(
                        user_id=current_user.id,
                        cv_profile_id=latest_cv.id,
                        title=job_data.get('title'),
                        company=job_data.get('company'),
                        location=job_data.get('location'),
                        job_url=job_url,
                        source='Adzuna',
                        description=job_data.get('description')
                    )
                    db.add(job_match)
                    existing_urls.add(job_url)
                    new_jobs_added += 1
            if new_jobs_added > 0:
                db.commit()
        return {"success": True, "jobs_found": new_jobs_added, "message": f"Successfully added {new_jobs_added} new jobs."}
    except Exception as e:
        db.rollback()
        print(f"❌ Job discovery error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"The job discovery process failed: {e}")


# --- Cover Letter Generation Endpoint ---
@app.post("/api/jobs/{job_id}/generate-cover-letter", response_model=dict)
async def generate_cover_letter_endpoint(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Generates a cover letter for a specific job using the user's CV and Cohere."""
    latest_cv = db.query(models.CVProfile).filter(models.CVProfile.user_id == current_user.id).order_by(models.CVProfile.created_at.desc()).first()
    if not latest_cv or not latest_cv.full_text:
        raise HTTPException(status_code=400, detail="No CV text found. Please upload a CV first.")

    job = db.query(models.JobMatch).filter(models.JobMatch.id == job_id, models.JobMatch.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    prompt = f"""
    Based on the following CV and Job Description, write a professional and compelling cover letter.
    The tone should be confident but not arrogant. The letter should highlight the most relevant skills from the CV that match the job description.

    --- MY CV ---
    {latest_cv.full_text}

    --- JOB DESCRIPTION ---
    Job Title: {job.title}
    Company: {job.company}
    Description: {job.description}

    --- COVER LETTER ---
    """

    try:
        response = co.generate(
            model='command-r-plus',
            prompt=prompt,
            max_tokens=1000,
            temperature=0.6,
        )
        cover_letter = response.generations[0].text
        return {"cover_letter": cover_letter}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")


# --- Job matches endpoint ---
@app.get("/api/jobs/matches", response_model=List[schemas.JobResponse])
async def get_job_matches(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Retrieves matched jobs for the current user from the database."""
    matches = db.query(models.JobMatch).filter(models.JobMatch.user_id == current_user.id).order_by(models.JobMatch.discovered_at.desc()).limit(limit).all()
    response_jobs = [
        schemas.JobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            salary=job.salary,
            score=job.match_score,
            job_url=job.job_url,
            source=job.source
        ) for job in matches
    ]
    return response_jobs
