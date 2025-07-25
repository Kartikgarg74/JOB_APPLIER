# Testing Guide

This project uses **pytest** for backend (Python) and **Jest**/**Playwright** for frontend (TypeScript/React) testing. All tests are run in CI via GitHub Actions.

## Table of Contents
- [Backend Testing (pytest)](#backend-testing-pytest)
- [Frontend Testing (Jest & Playwright)](#frontend-testing-jest--playwright)
- [Coverage Reports](#coverage-reports)
- [Continuous Integration (CI)](#continuous-integration-ci)
- [Fixtures & Mocks](#fixtures--mocks)
- [Test Structure](#test-structure)

---

## Backend Testing (pytest)

- **Unit tests:**
  - Located in `tests/` directories in each agent package (e.g., `test_job_scraper_agent.py`).
  - Run with:
    ```bash
    pytest
    ```
- **Integration tests:**
  - Test agent interactions and API endpoints.
  - Use pytest fixtures and mocks for DB/services.
- **End-to-End (E2E) tests:**
  - See `apps/job_applier_agent/tests/test_e2e_application_flow.py` for a full job application flow.

## Frontend Testing (Jest & Playwright)

- **Unit tests:**
  - Located in `frontend/__tests__/` or colocated with components.
  - Run with:
    ```bash
    cd frontend
    npm run test
    ```
- **Integration tests:**
  - Test component/API integration, often colocated with components.
- **End-to-End (E2E) tests:**
  - Located in `frontend/e2e/` (e.g., `job_application.spec.ts`).
  - Uses Playwright:
    ```bash
    cd frontend
    npx playwright test
    ```
  - Install Playwright browsers if needed:
    ```bash
    npx playwright install
    ```

## Coverage Reports

- **Backend:**
  - Run: `pytest --cov=packages --cov=apps --cov-report=html`
  - View HTML report in `htmlcov/`.
- **Frontend:**
  - Run: `npm run test -- --coverage`
  - View HTML report in `frontend/coverage/lcov-report/index.html`.

## Continuous Integration (CI)

- All tests and coverage are run on push/PR to `main` via GitHub Actions (`.github/workflows/ci.yml`).
- Coverage reports are uploaded as artifacts.

## Fixtures & Mocks

- **Backend:**
  - Use `pytest` fixtures for DB, user data, and agent mocks.
  - Use `unittest.mock.patch` for external service mocking.
- **Frontend:**
  - Use Jest mocks for API calls and Playwright fixtures for E2E setup.

## Test Structure

- **Backend:**
  - `test_*.py` files in each agent's `tests/` directory.
  - E2E tests in `apps/job_applier_agent/tests/`.
- **Frontend:**
  - Unit/integration: `frontend/__tests__/` or colocated.
  - E2E: `frontend/e2e/`

---

For questions or to contribute new tests, see the [README.md](../README.md) or open an issue.
