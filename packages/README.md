# Packages

This directory contains shared packages and modules used across different applications within the Job Applier project. Each subdirectory represents a distinct package with a specific set of functionalities.

## Directory Structure

- `agents/`: Contains various AI agents responsible for specific tasks within the job application process.
- `database/`: Handles database models, migrations, and session management.
- `errors/`: Custom exception classes for handling application-specific errors.
- `notifications/`: Services for sending various types of notifications (e.g., email, SMS, in-app).
- `utilities/`: General utility functions and helpers.

## Guidelines

- **Modularity**: Each package should be self-contained and focus on a single responsibility.
- **Reusability**: Design components within packages to be easily reusable across different parts of the system.
- **Clear APIs**: Define clear and well-documented APIs for all public functions and classes within each package.
- **Testing**: Each package should have its own set of unit and integration tests.
- **Documentation**: Maintain a `README.md` file within each package directory explaining its purpose, usage, and key components.