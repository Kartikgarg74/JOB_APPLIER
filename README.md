# JOB APPLIER

## Overview
An autonomous job application system that optimizes and automates the job search process using AI agents, a modular Python backend, and a Next.js/React frontend. The project is containerized with Docker and supports free-tier deployment.

---

## Technology Stack
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI (Python), modular microservices
- **Database:** PostgreSQL
- **Queue:** Upstash Redis (cloud), Celery
- **Monitoring:** Prometheus, Grafana, Loki
- **Testing:** Pytest (backend), Jest/Playwright (frontend)
- **AI/ML:** spaCy, SentenceTransformers, custom agents
- **Orchestration:** Docker Compose, Nginx

---

## Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop) (with Compose)
- [Node.js](https://nodejs.org/) (for local frontend dev)
- Upstash Redis account (free tier)

---

## Environment Variables
Create a `.env` file in the project root with:
```
UPSTASH_REDIS_REST_URL=your-upstash-redis-url
UPSTASH_REDIS_REST_TOKEN=your-upstash-redis-token
# Add any other required secrets here
```

---

## Project Structure
```
project-root/
├── apps/
│   ├── agent_orchestration_service/
│   ├── ats_service/
│   ├── user_service/
│   └── job_applier_agent/
├── packages/           # Shared agents, utilities, config, database
├── frontend/           # Next.js app
├── data/               # Nginx config, monitoring data
├── tools/              # Monitoring configs, scripts
├── docker-compose.yml
├── README.md
└── ...
```

---

## Quick Start (Docker)
1. **Build all services:**
   ```sh
   docker compose build --no-cache | tee docker-compose.log
   ```
2. **Start the stack:**
   ```sh
   docker compose up --remove-orphans --force-recreate | tee docker-compose.log
   ```
3. **Access the app:**
   - Frontend: [http://localhost](http://localhost)
   - API Endpoints:
     - `/api/agent/` → Agent Orchestration
     - `/api/ats/` → ATS Service
     - `/api/user/` → User Service
   - Monitoring:
     - Grafana: [http://localhost:3000](http://localhost:3000) (default admin/admin)
     - Prometheus: [http://localhost:9090](http://localhost:9090)

---

## Development
- **Frontend:**
  ```sh
  cd frontend
  npm install
  npm run dev
  ```
- **Backend (example):**
  ```sh
  cd apps/agent_orchestration_service
  uvicorn src.main:app --reload --port 8002
  # Repeat for other services as needed
  ```

---

## Testing
- **Backend:**
  ```sh
  cd apps/job_applier_agent
  pytest
  ```
- **Frontend:**
  ```sh
  cd frontend
  npm run test
  npx playwright test
  ```

---

## Troubleshooting
- **ModuleNotFoundError: No module named 'packages'**
  - Ensure Docker build context is set to project root in `docker-compose.yml`.
  - Each backend Dockerfile must copy `../../packages` and set `PYTHONPATH=/app`.
- **Redis connection errors:**
  - Make sure `.env` has correct Upstash Redis credentials.
- **Port conflicts:**
  - Dashboard runs on 3001 (container 3000), Nginx on 80, Grafana on 3000, Prometheus on 9090.
- **Nginx 502/504 errors:**
  - Check backend service logs for crashes or import errors.
- **Build errors (input/output error):**
  - Clean up large/unused files, ensure enough disk space, and avoid copying `.venv` or `node_modules` into containers.

---

## Contributing
Pull requests and issues are welcome! Please see the `CONTRIBUTING.md` for guidelines.

---

## License
MIT
