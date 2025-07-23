# Proposed Microservices Architecture for Job Applier Agent

## 1. Introduction

This document outlines a proposed microservices architecture for the Job Applier Agent application. The current application is structured as a monolithic FastAPI service, which, while modular at the API router level, can present challenges for scalability, independent deployment, and fault isolation as the system grows. Refactoring into microservices will address these concerns and lay the groundwork for future enhancements.

## 2. Goals of Microservices Adoption

*   **Improved Scalability**: Each service can be scaled independently based on its specific load requirements.
*   **Independent Deployment**: Services can be developed, deployed, and updated without affecting other parts of the system.
*   **Enhanced Resilience**: Failure in one service is less likely to impact the entire application.
*   **Technology Heterogeneity**: Different services can use different technologies best suited for their tasks (though initially, all will remain Python/FastAPI).
*   **Clearer Ownership**: Teams can own specific services, leading to better organization and faster development cycles.

## 3. Proposed Service Boundaries

Based on the existing API routers in `apps/job_applier_agent/src/main.py`, the following distinct microservices are proposed:

*   **User Service**: Manages user authentication, registration, and profile data.
    *   **Current Mapping**: `src/user_api.py` and `src/profile_api.py` (potentially merged or kept separate based on domain).
*   **Agent Orchestration Service**: Coordinates and executes various job application agents (e.g., resume parsing, ATS scoring, application automation).
    *   **Current Mapping**: `src/agent_api.py` and the `packages/agents` module.
*   **ATS Service**: Handles ATS (Applicant Tracking System) related functionalities, such as scoring and compatibility checks.
    *   **Current Mapping**: `src/ats_api.py`.
*   **Notification Service**: Manages sending notifications and alerts to users.
    *   **Current Mapping**: `packages/notifications/notification_service.py` (this would become a dedicated service).

## 4. New Project Structure (within Monorepo)

To maintain a cohesive development environment, these microservices will reside within the existing monorepo structure under the `apps/` directory. Each service will have its own dedicated directory, `Dockerfile`, `requirements.txt`, and `main.py`.

```
project-root/
├── apps/
│   ├── dashboard/          # Existing Next.js frontend
│   ├── user_service/       # New User Service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── agent_orchestration_service/ # New Agent Orchestration Service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── ats_service/        # New ATS Service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── notification_service/ # New Notification Service
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── job_applier_agent/  # Original monolithic app (will be refactored/removed)
│       └── ...
├── packages/               # Shared packages (e.g., common_types, errors, utilities)
│   └── ...
├── docs/
│   └── architecture.md     # This document
└── ...
```

## 5. Inter-service Communication: Message Queuing

To improve responsiveness and scalability, especially for long-running agent tasks, a message queue will be introduced for asynchronous task processing. This will decouple services and enable robust, scalable communication.

*   **Recommendation**: Celery with Redis or RabbitMQ as a broker.
*   **Mechanism**: Services will publish messages (e.g., "process job application") to the message queue, and worker services will consume these messages asynchronously.
*   **Benefits**: Decoupling, improved responsiveness of API endpoints, load leveling, and easier scaling of worker processes.

## 6. Database Strategy

Each microservice will ideally own its data. However, for initial implementation, a shared database with clear schema ownership per service can be considered to reduce complexity. Long-term, dedicated databases per service are preferred.

*   **Optimization**: For each service's database interactions:
    *   **Schema Review**: Continuously review and optimize database schemas.
    *   **Indexing**: Implement appropriate indexing strategies for frequently queried columns.
    *   **Query Optimization**: Profile and optimize slow queries.
    *   **Connection Pooling**: Implement connection pooling (e.g., using SQLAlchemy's connection pool) to efficiently manage database connections and reduce overhead.

## 7. Configuration Management

Centralized and externalized configuration is crucial for managing different environments (development, staging, production) and for independent service deployment.

*   **Recommendation**: Environment variables for sensitive data (API keys, database credentials) and a configuration management library (e.g., `python-decouple`, `Dynaconf`, or simple JSON/YAML files) for other settings.
*   **Mechanism**: Each service will load its configuration from a central source or environment-specific files, ensuring that no sensitive information is hardcoded.

## 8. API Versioning

Implementing API versioning will allow for backward compatibility as individual service APIs evolve, preventing breaking changes for consumers.

*   **Recommendation**: URL-based versioning (e.g., `/api/v1/users`, `/api/v2/users`).
*   **Mechanism**: Each service's API endpoints will include a version prefix, allowing for parallel deployment of different API versions during transitions.

## 9. Next Steps

1.  **Detailed Design**: Create detailed design documents for each proposed microservice, including API contracts and data models.
2.  **Service Creation**: Begin creating the new service directories and moving relevant code.
3.  **Message Queue Setup**: Set up a message queue infrastructure (e.g., Docker Compose for Redis/RabbitMQ and Celery workers).
4.  **Refactor and Integrate**: Gradually refactor the existing monolithic application into the new services, ensuring proper inter-service communication.
5.  **Testing**: Implement comprehensive integration and end-to-end tests for the new architecture.