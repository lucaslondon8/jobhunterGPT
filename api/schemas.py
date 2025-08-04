# api/schemas.py

from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
import uuid

# --- Schemas for User Authentication ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    # The user ID is a UUID, so it should be a string.
    id: str
    email: EmailStr
    is_active: bool

    class Config:
        # Renamed from orm_mode for Pydantic v2
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

# --- Existing Schemas ---
class StatsResponse(BaseModel):
    applications_sent: int
    response_rate: float
    jobs_discovered: int
    email_discovery_rate: float
    time_saved: int

class JobResponse(BaseModel):
    # FIX: The job ID from the database is a UUID string, not an integer.
    id: str | None = None
    title: str | None = None
    company: str | None = None
    location: str | None = None
    salary: str | None = None
    score: float | None = None
    match_strength: str | None = None
    application_priority: str | None = None
    contact_email: str | None = None
    source: str | None = None
    job_url: str | None = None
    description: Optional[str] = None

class CVAnalysisResponse(BaseModel):
    success: bool
    analysis: Dict[str, Any]
    message: str

class ApplicationRequest(BaseModel):
    # FIX: The job_id needs to be a string to match the JobResponse ID.
    job_id: str
    custom_message: str | None = None
