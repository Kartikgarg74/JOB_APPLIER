# Dependency Management Guide

## Overview
This project uses a simplified dependency management approach to avoid complex version conflicts while maintaining functionality.

## Core Dependencies

### Main Requirements (`requirements.txt`)
The main requirements file contains all essential dependencies for the core application:

```bash
pip install -r requirements.txt
```

**Key Changes Made:**
- ✅ **PyJWT**: Updated from `2.8.0` to `2.9.0` for Redis compatibility
- ✅ **Redis**: Downgraded from `5.3.1` to `5.0.1` for better compatibility
- ✅ **Removed**: Complex NLP libraries (spacy, nltk) to avoid conflicts
- ✅ **Simplified**: Removed unnecessary transitive dependencies

### Optional NLP Dependencies (`requirements-nlp.txt`)
For advanced NLP features, install separately:

```bash
pip install -r requirements-nlp.txt
```

**Note:** These are optional and can cause dependency conflicts. Install only if needed.

## Service-Specific Requirements

All service directories have their own `requirements.txt` files that mirror the main requirements:

- `apps/ats_service/requirements.txt`
- `apps/job_applier_agent/requirements.txt`
- `apps/user_service/requirements.txt`
- `apps/agent_orchestration_service/requirements.txt`
- `packages/message_queue/requirements.txt`

## Dependency Conflicts Resolved

### 1. PyJWT vs Redis Conflict
**Problem:** `redis==5.3.1` required `PyJWT>=2.9.0` but we had `PyJWT==2.8.0`
**Solution:** Updated PyJWT to `2.9.0` and downgraded Redis to `5.0.1`

### 2. Complex Dependency Graph
**Problem:** Too many interdependent packages causing resolution issues
**Solution:** Simplified to core dependencies only

### 3. NLP Library Conflicts
**Problem:** spacy and nltk had complex dependency trees
**Solution:** Moved to optional separate requirements file

## Installation Instructions

### For Development
```bash
# Install core dependencies
pip install -r requirements.txt

# Optional: Install NLP libraries (only if needed)
pip install -r requirements-nlp.txt
```

### For Production Deployment
```bash
# Install only core dependencies
pip install -r requirements.txt
```

### For Individual Services
```bash
# Navigate to service directory
cd apps/job_applier_agent
pip install -r requirements.txt
```

## Verification

Test that dependencies are compatible:
```bash
pip install -r requirements.txt --dry-run
```

## Troubleshooting

### If you encounter dependency conflicts:

1. **Clear pip cache:**
   ```bash
   pip cache purge
   ```

2. **Use virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install dependencies one by one:**
   ```bash
   pip install fastapi==0.111.0
   pip install uvicorn==0.35.0
   # ... continue with other packages
   ```

4. **For Render deployment:**
   - Use the simplified `requirements.txt`
   - Avoid installing NLP libraries unless absolutely necessary
   - Consider using Docker for complex dependency management

## Version Compatibility Matrix

| Package | Version | Compatible With |
|---------|---------|-----------------|
| PyJWT | 2.9.0 | Redis 5.0.1+ |
| Redis | 5.0.1 | Celery 5.3.6 |
| Celery | 5.3.6 | Kombu 5.3.4+ |
| FastAPI | 0.111.0 | Uvicorn 0.35.0 |
| Pydantic | 2.7.3 | FastAPI 0.111.0 |

## Notes

- All versions are pinned to exact versions for reproducibility
- NLP libraries are optional and can be installed separately
- The simplified approach prioritizes deployment success over advanced features
- Consider using Docker for production deployments to avoid environment-specific issues
