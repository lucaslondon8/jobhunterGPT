#!/bin/bash
# setup.sh - Complete setup script for JobHuntGPT multi-user system

echo "🚀 Setting up JobHuntGPT Multi-User System..."
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p api/routers
mkdir -p migrations/versions
mkdir -p output
mkdir -p assets
mkdir -p cover_letters
mkdir -p frontend/src/components

echo "✅ Directory structure created"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate secure random keys
    SECRET_KEY=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -hex 16)
    
    # Update .env with generated keys
    sed -i "s/your-super-secret-jwt-key-change-in-production/$SECRET_KEY/" .env
    sed -i "s/your_secure_database_password_here/$POSTGRES_PASSWORD/" .env
    
    echo "🔐 Generated secure keys in .env file"
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - MAILGUN_API_KEY"
    echo "   - MAILGUN_DOMAIN" 
    echo "   - COHERE_API_KEY"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Initialize database migrations
echo "🗄️  Setting up database migrations..."
if [ ! -d "migrations" ]; then
    # Create alembic configuration
    cat > alembic.ini << 'EOF'
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql://jobhuntgpt:password@localhost:5432/jobhuntgpt

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

    # Create migrations directory structure
    mkdir -p migrations/versions
    
    # Create env.py for alembic
    cat > migrations/env.py << 'EOF'
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your models
from api.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_url():
    return os.getenv("DATABASE_URL", "postgresql://jobhuntgpt:password@localhost:5432/jobhuntgpt")

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
EOF

    echo "✅ Database migrations initialized"
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose up -d postgres redis

echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T postgres psql -U jobhuntgpt -d jobhuntgpt -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"

# Start the full stack
echo "🚀 Starting full JobHuntGPT stack..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 15

# Check service health
echo "🏥 Checking service health..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "⚠️  Backend health check failed"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is accessible"
else
    echo "⚠️  Frontend not accessible"
fi

echo ""
echo "🎉 JobHuntGPT Multi-User Setup Complete!"
echo "========================================"
echo ""
echo "🌐 Services Available:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo "   • Database:  localhost:5432"
echo ""
echo "📝 Next Steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Visit http://localhost:3000 to access the dashboard"
echo "   3. Create an account and upload your CV"
echo "   4. Start discovering jobs!"
echo ""
echo "🔧 Management Commands:"
echo "   • View logs:     docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart:       docker-compose restart"
echo ""

---
# run-dev.sh - Development mode startup
#!/bin/bash

echo "🔥 Starting JobHuntGPT in Development Mode..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Run setup.sh first."
    exit 1
fi

# Load environment variables
source .env

# Start database and redis only
echo "🗄️  Starting database and Redis..."
docker-compose up -d postgres redis

echo "⏳ Waiting for services..."
sleep 5

# Install Python dependencies in virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start backend in development mode
echo "🚀 Starting FastAPI backend..."
export PYTHONPATH=.
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Celery worker
echo "👷 Starting Celery worker..."
celery -A api.tasks worker --loglevel=info &
CELERY_PID=$!

# Start React frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm install
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Development environment started!"
echo ""
echo "🌐 Services:"
echo "   • Frontend:  http://localhost:3000"
echo "   • Backend:   http://localhost:8000"
echo "   • API Docs:  http://localhost:8000/docs"
echo ""
echo "🔧 To stop all services:"
echo "   • Press Ctrl+C or run: kill $BACKEND_PID $CELERY_PID $FRONTEND_PID"
echo ""

# Keep script running
wait

---
# migrate.sh - Database migration helper
#!/bin/bash

echo "🗄️  Database Migration Helper"
echo "============================="

case "$1" in
    "init")
        echo "🏗️  Initializing database migrations..."
        alembic init migrations
        echo "✅ Migrations initialized"
        ;;
    "create")
        if [ -z "$2" ]; then
            echo "❌ Please provide a migration message"
            echo "Usage: ./migrate.sh create \"your migration message\""
            exit 1
        fi
        echo "📝 Creating new migration: $2"
        alembic revision --autogenerate -m "$2"
        echo "✅ Migration created"
        ;;
    "upgrade")
        echo "⬆️  Applying migrations..."
        alembic upgrade head
        echo "✅ Migrations applied"
        ;;
    "downgrade")
        if [ -z "$2" ]; then
            echo "⬇️  Downgrading one migration..."
            alembic downgrade -1
        else
            echo "⬇️  Downgrading to: $2"
            alembic downgrade "$2"
        fi
        echo "✅ Downgrade complete"
        ;;
    "history")
        echo "📜 Migration history:"
        alembic history
        ;;
    "current")
        echo "📍 Current migration:"
        alembic current
        ;;
    *)
        echo "Usage: ./migrate.sh {init|create|upgrade|downgrade|history|current}"
        echo ""
        echo "Commands:"
        echo "  init                 - Initialize migrations"
        echo "  create \"message\"     - Create new migration"
        echo "  upgrade              - Apply all pending migrations"
        echo "  downgrade [revision] - Downgrade migrations"
        echo "  history              - Show migration history"
        echo "  current              - Show current migration"
        exit 1
        ;;
esac

---
# deploy.sh - Production deployment script
#!/bin/bash

echo "🚀 Deploying JobHuntGPT to Production"
echo "===================================="

# Check if running on production environment
if [ "$ENVIRONMENT" != "production" ]; then
    echo "⚠️  Not in production environment. Set ENVIRONMENT=production"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Build production images
echo "🏗️  Building production images..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Pull latest images
echo "📥 Pulling latest images..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Start production stack
echo "🚀 Starting production stack..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend alembic upgrade head

# Health check
echo "🏥 Running health checks..."
for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    else
        echo "⏳ Waiting for backend... ($i/10)"
        sleep 10
    fi
done

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "⚠️  Frontend health check failed"
fi

echo ""
echo "🎉 Production Deployment Complete!"
echo "================================="
echo ""
echo "🌐 Production URLs:"
echo "   • Application: http://your-domain.com"
echo "   • API:         http://your-domain.com/api"
echo "   • Docs:        http://your-domain.com/docs"
echo ""
echo "📊 Monitoring Commands:"
echo "   • Logs:        docker-compose logs -f"
echo "   • Status:      docker-compose ps"
echo "   • Restart:     docker-compose restart"
echo ""

---
# docker-compose.prod.yml - Production overrides
version: '3.8'

services:
  backend:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    restart: always
    
  frontend:
    restart: always
    
  postgres:
    restart: always
    volumes:
      - /var/lib/postgresql/data:/var/lib/postgresql/data
    
  redis:
    restart: always
    
  # Add Nginx reverse proxy for production
  nginx:
    image: nginx:alpine
    container_name: jobhuntgpt-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: always

---
# nginx.prod.conf - Production Nginx configuration
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:80;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
    
    server {
        listen 80;
        server_name your-domain.com;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # API routes
        location /api {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Auth routes (stricter rate limiting)
        location /auth {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

---
# README.md - Complete documentation
# JobHuntGPT Multi-User System

🚀 **AI-Powered Job Application Automation with Multi-User Support**

JobHuntGPT automatically discovers, matches, and applies to relevant job opportunities using your existing CV analysis, job matching, and scraping modules, now enhanced with user authentication and database persistence.

## ✨ Features

### 🧠 **CV Analysis & Matching**
- **Universal CV Analysis**: Works with any CV using your existing `cv_analyzer.py`
- **Intelligent Job Matching**: Uses your proven `match_job.py` algorithm
- **Dynamic Profile Detection**: Adapts to different industries and experience levels

### 🔍 **Job Discovery**
- **Multi-Source Scraping**: Remote OK, Indeed UK, CryptoJobs, GitHub
- **Adaptive Targeting**: Job sites selected based on CV analysis
- **Real-Time Discovery**: Background job discovery with progress tracking

### 👥 **Multi-User Support**
- **Secure Authentication**: JWT-based authentication with FastAPI-Users
- **User Isolation**: Each user's data is completely isolated
- **Profile Management**: Multiple CV profiles per user

### 📧 **Email Automation**
- **Automatic Email Discovery**: Find hiring manager contacts
- **AI Cover Letters**: Generated using your existing Cohere integration
- **Email Sending**: Mailgun integration for reliable delivery
- **Response Tracking**: Track opens, clicks, and responses

### 📊 **Analytics & Tracking**
- **Performance Metrics**: Response rates, application success
- **Job Match Scoring**: Detailed scoring breakdown
- **Application History**: Complete audit trail

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │────│   FastAPI       │────│   PostgreSQL    │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                       ┌──────┴──────┐
                       │   Redis +   │
                       │   Celery    │
                       │ (Background)│
                       └─────────────┘
```

### Core Components

- **Frontend**: React dashboard with real-time updates
- **Backend**: FastAPI with your existing modules integrated
- **Database**: PostgreSQL with user isolation
- **Background Jobs**: Celery with Redis for job discovery
- **Email Service**: Mailgun integration
- **Authentication**: FastAPI-Users with JWT

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone and Setup**
```bash
git clone <your-repo>
cd jobhuntgpt-multiuser
chmod +x setup.sh
./setup.sh
```

2. **Configure Environment**
Edit `.env` file with your API keys:
```bash
MAILGUN_API_KEY=your_mailgun_key
MAILGUN_DOMAIN=your_domain
COHERE_API_KEY=your_cohere_key
```

3. **Start Services**
```bash
docker-compose up -d
```

4. **Access Application**
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs

## 🔧 Development

### Development Mode
```bash
./run-dev.sh
```

### Database Migrations
```bash
./migrate.sh create "Add new feature"
./migrate.sh upgrade
```

### View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f worker
```

## 📚 API Reference

### Authentication
```bash
# Register
POST /auth/register
{
  "email": "user@example.com",
  "password": "secure_password"
}

# Login
POST /auth/jwt/login
```

### CV Management
```bash
# Upload CV
POST /api/upload-cv
Content-Type: multipart/form-data

# Get CV Analysis
GET /api/cv-analysis
```

### Job Discovery
```bash
# Start Job Discovery
POST /api/jobs/discover
{
  "max_jobs": 50
}

# Get Job Matches
GET /api/jobs/matches?limit=20&min_score=0.3
```

### Applications
```bash
# Create Application
POST /api/applications
{
  "job_match_id": "uuid",
  "custom_message": "Optional custom message"
}

# Get Applications
GET /api/applications
```

## 🗄️ Database Schema

### Core Tables
- **users**: User accounts and preferences
- **cv_profiles**: CV analysis results per user
- **job_matches**: Discovered jobs with match scores
- **applications**: Application tracking and status

### Key Features
- **UUID Primary Keys**: Secure, non-sequential IDs
- **User Isolation**: Foreign key constraints ensure data isolation
- **JSON Fields**: Flexible storage for dynamic data
- **Indexes**: Optimized for performance

## 🔐 Security

### Authentication
- JWT tokens with secure secrets
- Password hashing with bcrypt
- User session management

### Data Protection
- User data isolation
- GDPR compliance features
- Secure password policies

### Rate Limiting
- API endpoint protection
- Authentication rate limiting
- DDoS protection

## 📧 Email Integration

### Mailgun Setup
1. Create Mailgun account
2. Verify domain
3. Add API key to `.env`

### Email Features
- **Automated Sending**: Background email delivery
- **Tracking**: Open and click tracking
- **Templates**: Customizable email templates
- **Response Handling**: Manual response tracking

## 🚀 Deployment

### Production Deployment
```bash
export ENVIRONMENT=production
./deploy.sh
```

### Recommended Platforms
- **Railway**: Easy deployment with PostgreSQL
- **DigitalOcean**: App Platform or Droplets
- **AWS**: ECS with RDS
- **Google Cloud**: Cloud Run with Cloud SQL

### Environment Variables
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/0
SECRET_KEY=your-jwt-secret
MAILGUN_API_KEY=your-mailgun-key
COHERE_API_KEY=your-cohere-key
```

## 📊 Monitoring

### Health Checks
- **Backend**: `/health` endpoint
- **Database**: Connection status
- **Redis**: Cache connectivity

### Logging
- **Application Logs**: Structured JSON logging
- **Error Tracking**: Detailed error capture
- **Performance Metrics**: Response time tracking

## 🔧 Customization

### Adding New Job Sources
1. Add scraper method to `RealJobScraper`
2. Update `determine_target_sources()` logic
3. Add to CV analysis targeting

### Custom Email Templates
1. Modify `_format_application_email()` in `email_service.py`
2. Add template variations
3. Customize per industry/role

### Enhanced Matching
1. Extend `RealJobMatcher` algorithms
2. Add new scoring factors
3. Implement ML-based matching

## 🐛 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check PostgreSQL status
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

**Email Sending Failed**
```bash
# Verify Mailgun credentials
curl -s --user 'api:YOUR_API_KEY' \
    https://api.mailgun.net/v3/YOUR_DOMAIN/messages \
    -F from='test@YOUR_DOMAIN' \
    -F to='test@example.com' \
    -F subject='Test' \
    -F text='Testing'
```

**Background Jobs Not Running**
```bash
# Check Celery worker
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

## 📈 Performance

### Optimization Tips
- Use database indexes effectively
- Implement caching for frequent queries
- Optimize job discovery batch sizes
- Use async operations for I/O

### Scaling
- Horizontal scaling with multiple workers
- Database read replicas
- Redis clustering
- CDN for static assets

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

Private License - All Rights Reserved

## 🆘 Support

For support, please contact:
- **Email**: support@jobhuntgpt.com
- **Documentation**: /docs
- **Issues**: GitHub Issues

---

**Built with your existing modules:**
- ✅ `cv_analyzer.py` - Universal CV analysis
- ✅ `match_job.py` - Intelligent job matching  
- ✅ `scrape_and_match.py` - Multi-source job discovery
- ✅ `generate_cover_letter.py` - AI cover letter generation
