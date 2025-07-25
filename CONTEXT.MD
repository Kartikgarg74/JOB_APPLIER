# Project Context: JOB_APPLIER

## Project Overview
An autonomous job application system built with TypeScript (51.4%) and Python (47.5%) that helps users optimize and automate their job search process.

## Technology Stack
- **Frontend**: Next.js, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python
- **Database**: PostgreSQL
- **Queue**: Redis, Celery
- **Monitoring**: Prometheus
- **Testing**: pytest
- **AI/ML**: Open to integration (currently evaluating options)

## Current Development Environment
- Development: Local setup
- Deployment: Free-tier services
- Open to importing pre-trained models and APIs
- CI/CD: Basic GitHub Actions

## AI Model Integration Options
1. **Resume Parsing**:
   - OpenAI GPT-4 API
   - HuggingFace Transformers
   - spaCy NER models

2. **ATS Scoring**:
   - OpenAI Embeddings
   - SentenceTransformers
   - Custom trained models

3. **Job Matching**:
   - OpenAI Embeddings
   - Word2Vec/Doc2Vec
   - BERT/RoBERTa

## Project Structure
```
project-root/
├── apps/
│   └── job-applier-agent/     # Main application
├── packages/
│   ├── agents/                # Core AI agents
│   ├── utilities/             # Shared utilities
│   ├── types/                 # Type definitions
│   ├── config/                # Configurations
│   └── database/              # DB schemas
```

## Current Completion Status
- Overall: 55%
- Frontend: 80%
- Backend Core: 65%
- AI Agents: 35%
- Testing: 40%

## Development Priorities
1. Core AI agent implementation
2. Job scraping automation
3. Advanced NLP features
4. Learning agent functionality
5. Comprehensive testing
6. Error handling

## Notes for AI Assistance
- Prefer production-ready solutions
- Consider free-tier limitations
- Focus on maintainable code
- Prioritize TypeScript/Python best practices
- Consider API rate limits
- Optimize for deployment on free tiers
