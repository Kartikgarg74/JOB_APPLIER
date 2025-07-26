# Dependency Management Guide

## Overview
This project uses a comprehensive dependency management approach that includes all required NLP libraries for resume parsing functionality.

## Core Dependencies

### Main Requirements (`requirements.txt`)
The main requirements file contains all essential dependencies including NLP libraries:

```bash
pip install -r requirements.txt
```

**Key Changes Made:**
- ✅ **PyJWT**: Updated from `2.8.0` to `2.9.0` for Redis compatibility
- ✅ **Redis**: Downgraded from `5.3.1` to `5.0.1` for better compatibility
- ✅ **spacy**: Updated to `3.8.7` for Python 3.12 compatibility
- ✅ **nltk**: Set to `3.8.1` for NLP functionality
- ✅ **Stripe**: Added `8.10.0` for monetization support
- ✅ **beautifulsoup4**: Added `4.12.3` for web scraping functionality

### Optional Advanced NLP Dependencies (`requirements-nlp.txt`)
For additional NLP features beyond the core requirements:

```bash
pip install -r requirements-nlp.txt
```

**Includes:**
- textblob==0.17.1
- scikit-learn==1.4.0
- sentence-transformers==2.5.1
- transformers==4.38.2
- torch==2.2.0

## Service-Specific Requirements

Each service has its own requirements.txt file that matches the main requirements:

- `apps/ats_service/requirements.txt`
- `apps/job_applier_agent/requirements.txt`
- `apps/user_service/requirements.txt`
- `apps/agent_orchestration_service/requirements.txt`
- `packages/message_queue/requirements.txt`

## Dependency Conflicts Resolved

### 1. PyJWT vs Redis Conflict
**Problem**: `redis==5.3.1` required `PyJWT>=2.9.0` but we had `PyJWT==2.8.0`
**Solution**: Updated PyJWT to `2.9.0` and downgraded Redis to `5.0.1`

### 2. spacy vs fastapi-cli Conflict
**Problem**: `spacy==3.7.4` required `typer<0.10.0` but `fastapi-cli` required `typer>=0.12.3`
**Solution**: Updated spacy to `3.8.7` which uses `typer<1.0.0,>=0.3.0` (compatible with fastapi-cli)

### 3. Python 3.12 Compatibility
**Problem**: Older spacy versions had compilation issues with Python 3.12
**Solution**: Used spacy `3.8.7` which has pre-compiled wheels for Python 3.12

## Installation Instructions

### For Basic Setup (Recommended)
```bash
# Install all dependencies including NLP libraries
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, sqlalchemy, celery, redis, spacy, nltk; print('All dependencies installed successfully!')"
```

### For Advanced NLP Features
```bash
# Install core dependencies first
pip install -r requirements.txt

# Then install additional NLP dependencies
pip install -r requirements-nlp.txt

# Download spacy models (optional)
python -m spacy download en_core_web_sm
```

### For Development
```bash
# Install all dependencies including development tools
pip install -r requirements.txt
pip install -r requirements-nlp.txt
pip install pytest black flake8 mypy
```

## Environment Variables

Create a `.env` file with:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Redis
REDIS_URL=redis://localhost:6379

# Stripe (for monetization)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# OpenAI
OPENAI_API_KEY=sk-...

# Other services
GOOGLE_API_KEY=...
MAILGUN_API_KEY=...
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'spacy'**
   - Solution: Install dependencies: `pip install -r requirements.txt`

2. **Redis connection errors**
   - Solution: Ensure Redis is running and `REDIS_URL` is set correctly

3. **Database connection errors**
   - Solution: Check `DATABASE_URL` and ensure PostgreSQL is running

4. **Stripe billing errors**
   - Solution: Verify `STRIPE_SECRET_KEY` and `STRIPE_PUBLISHABLE_KEY` are set

5. **spacy model download errors**
   - Solution: Run `python -m spacy download en_core_web_sm`

### Dependency Conflicts

If you encounter dependency conflicts:

1. **Clear existing environment**:
   ```bash
   pip uninstall -r requirements.txt -y
   pip cache purge
   ```

2. **Install fresh**:
   ```bash
   pip install -r requirements.txt
   ```

3. **For additional NLP features**:
   ```bash
   pip install -r requirements-nlp.txt
   ```

## Production Deployment

### Docker (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
export REDIS_URL="redis://..."

# Run services
python apps/job_applier_agent/src/main.py
```

## Version Compatibility Matrix

| Component | Version | Compatible With |
|-----------|---------|-----------------|
| FastAPI | 0.111.0 | Python 3.8+ |
| SQLAlchemy | 2.0.30 | Python 3.8+ |
| Redis | 5.0.1 | Python 3.8+ |
| Celery | 5.3.6 | Python 3.8+ |
| PyJWT | 2.9.0 | Python 3.6+ |
| spacy | 3.8.7 | Python 3.8+ |
| nltk | 3.8.1 | Python 3.7+ |
| Stripe | 8.10.0 | Python 3.7+ |
| beautifulsoup4 | 4.12.3 | Python 3.7+ |

## Security Notes

- All sensitive data should be stored in environment variables
- API keys should never be committed to version control
- Use `.env` files for local development only
- In production, use proper secret management systems

## Performance Considerations

- Redis is used for caching and message queuing
- PostgreSQL is used for persistent data storage
- Celery workers handle background tasks
- spacy provides efficient NLP processing
- Consider using connection pooling for database connections

## Monitoring

The application includes:
- Prometheus metrics via `prometheus-client`
- Structured logging via `loguru`
- Health check endpoints
- Rate limiting via `fastapi-limiter`

## Support

For dependency-related issues:
1. Check this documentation
2. Review the error messages carefully
3. Try the troubleshooting steps above
4. Create an issue with detailed error information

## NLP Features

The project includes comprehensive NLP capabilities:

### Resume Parsing
- **spacy**: Named Entity Recognition (NER) for extracting names, companies, dates
- **nltk**: Tokenization, part-of-speech tagging, chunking
- **Custom extraction**: Skills, experience, education, certifications

### ATS Scoring
- Keyword matching and scoring
- Skills alignment analysis
- Experience relevance scoring

### Job Matching
 - Semantic similarity using embeddings
 - Skills-based matching
 - Experience level alignment

### Web Scraping
 - **beautifulsoup4**: HTML parsing for job scraping
 - **requests**: HTTP requests for web scraping
 - Rate limiting and proxy rotation
 - Robots.txt compliance checking
