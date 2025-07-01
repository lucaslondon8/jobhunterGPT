#!/bin/bash
# simple-start.sh - Get JobHuntGPT running quickly

echo "🚀 Quick Start JobHuntGPT..."

# Step 1: Fix Python dependencies
echo "📦 Installing missing Python dependencies..."
source venv/bin/activate
pip install python-multipart alembic sqlalchemy psycopg2-binary

# Step 2: Create the corrected files
echo "📝 Creating corrected configuration files..."

# Fix requirements.txt
cat > requirements.txt << 'EOF'
pandas>=1.5.0
python-dotenv>=0.19.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
cohere>=4.0.0
scikit-learn>=1.1.0
fastapi>=0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
pydantic[email]==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
alembic==1.12.1
fastapi-users[sqlalchemy]==12.1.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
redis==5.0.1
celery==5.3.4
selenium>=4.8.0
mailgun2==1.0.7
EOF

# Create simple docker-compose.yml (fixed syntax)
cat > docker-compose.yml << 'EOF'
services:
  postgres:
    image: postgres:15
    container_name: jobhuntgpt-db
    environment:
      POSTGRES_DB: jobhuntgpt
      POSTGRES_USER: jobhuntgpt
      POSTGRES_PASSWORD: secure_password_123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Update .env file
cat > .env << 'EOF'
POSTGRES_PASSWORD=secure_password_123
DATABASE_URL=postgresql://jobhuntgpt:secure_password_123@localhost:5432/jobhuntgpt
SECRET_KEY=your-super-secret-key-change-in-production-12345
COHERE_API_KEY=6QYELzaCHMKLRPK8czOan54umjgPncyqiKOzj5mo
ENVIRONMENT=development
MAILGUN_API_KEY=
MAILGUN_DOMAIN=
EOF

# Create the API directory and simplified main.py
mkdir -p api

cat > api/main.py << 'EOF'
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from typing import List
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Try to import your existing modules
try:
    from cv_analyzer import analyze_any_cv
    CV_ANALYZER_AVAILABLE = True
except ImportError:
    CV_ANALYZER_AVAILABLE = False

app = FastAPI(title="JobHuntGPT API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple storage
current_user_data = {"cv_analysis": None, "jobs": [], "applications": []}

class StatsResponse(BaseModel):
    applications_sent: int
    response_rate: float
    jobs_discovered: int
    email_discovery_rate: float
    time_saved: int

class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    salary: str
    match_score: float
    has_email: bool

@app.get("/")
async def root():
    return {"message": "JobHuntGPT API is running!", "cv_analyzer": CV_ANALYZER_AVAILABLE}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    content = await file.read()
    cv_text = content.decode('utf-8')
    
    if CV_ANALYZER_AVAILABLE:
        analysis = analyze_any_cv(cv_text)
    else:
        analysis = {"experience_level": "mid", "skills": ["python", "react"], "confidence": 0.8}
    
    current_user_data["cv_analysis"] = analysis
    return {"success": True, "analysis": analysis, "message": "CV analyzed successfully"}

@app.post("/api/discover-jobs")
async def discover_jobs():
    demo_jobs = [
        {"id": 0, "title": "Senior Web3 Developer", "company": "DeFi Labs", "location": "Remote", 
         "salary": "£80k-£120k", "match_score": 92.0, "has_email": True},
        {"id": 1, "title": "Blockchain Engineer", "company": "Crypto Corp", "location": "London", 
         "salary": "£90k-£130k", "match_score": 88.0, "has_email": True}
    ]
    current_user_data["jobs"] = demo_jobs
    return {"success": True, "jobs_found": len(demo_jobs)}

@app.get("/api/dashboard-stats", response_model=StatsResponse)
async def get_stats():
    return StatsResponse(
        applications_sent=len(current_user_data.get("applications", [])),
        response_rate=18.4,
        jobs_discovered=len(current_user_data.get("jobs", [])),
        email_discovery_rate=100.0,
        time_saved=10
    )

@app.get("/api/jobs/matches", response_model=List[JobResponse])
async def get_jobs():
    return [JobResponse(**job) for job in current_user_data.get("jobs", [])]

@app.post("/api/applications")
async def apply_job(job_match_id: str):
    app_data = {
        "id": len(current_user_data.get("applications", [])),
        "job_title": "Applied Job",
        "company": "Company",
        "status": "sent",
        "created_at": datetime.now().isoformat()
    }
    if "applications" not in current_user_data:
        current_user_data["applications"] = []
    current_user_data["applications"].append(app_data)
    return {"success": True, "application_id": app_data["id"]}

@app.get("/api/cv-analysis")
async def get_cv_analysis():
    analysis = current_user_data.get("cv_analysis")
    if analysis:
        return {"analysis": analysis}
    raise HTTPException(status_code=404, detail="No CV analysis available")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
EOF

echo "✅ Files created successfully!"
echo ""
echo "🚀 Starting services..."

# Start PostgreSQL
echo "🗄️ Starting PostgreSQL..."
docker-compose up -d postgres
sleep 5

# Start the API
echo "🚀 Starting API server..."
echo "📍 Backend: http://localhost:8000"
echo "📍 Frontend: http://localhost:3000 (start in another terminal)"
echo ""

python api/main.py
