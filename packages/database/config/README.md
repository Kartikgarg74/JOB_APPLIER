# Database Configuration Module

## Purpose
This module (`config.py`) is responsible for setting up the database connection and session management for the application. It centralizes the configuration required to interact with the SQLAlchemy ORM.

## Dependencies
- `sqlalchemy.orm.sessionmaker`: For creating session factories.
- `sqlalchemy.ext.declarative.declarative_base`: For defining declarative models.
- `sqlalchemy.create_engine`: For creating the database engine.
- `packages.config.settings.settings`: To import application settings, specifically the `DATABASE_URL`.

## Key Components

### `SQLALCHEMY_DATABASE_URL`
- **Purpose**: Stores the database connection string, retrieved from the application's settings (`settings.DATABASE_URL`). This URL dictates which database system (e.g., SQLite, PostgreSQL) and where (e.g., file path, host) the application connects to.

### `engine`
- **Purpose**: An instance of `sqlalchemy.create_engine` that represents the core interface to the database. It's configured with the `SQLALCHEMY_DATABASE_URL` and `connect_args={"check_same_thread": False}` for SQLite, which is necessary when using SQLite with multiple threads (common in web applications).

### `SessionLocal`
- **Purpose**: A session factory created using `sessionmaker`. This factory is used to create individual `Session` objects, which are the primary way to interact with the database (e.g., querying, adding, updating, deleting data). It's configured with:
  - `autocommit=False`: Transactions are not automatically committed.
  - `autoflush=False`: Changes are not automatically flushed to the database.
  - `bind=engine`: Binds the session to the created database engine.

### `Base`
- **Purpose**: An instance of `declarative_base()`. This is the base class that all SQLAlchemy ORM models (tables) in the application will inherit from. It provides the declarative mapping functionality, allowing Python classes to be mapped to database tables.

## Workflow
1. The module imports necessary components from SQLAlchemy and the application's settings.
2. It retrieves the database URL from `settings.DATABASE_URL`.
3. An `engine` is created using this URL, establishing the connection to the database.
4. A `SessionLocal` factory is configured and bound to the `engine`, ready to create database sessions.
5. A `Base` class is defined, which will serve as the foundation for all ORM models.

## Usage
This module is typically imported by other parts of the application that need to interact with the database:
- ORM models (`models.py`, `job_data_model.py`, `user_data_model.py`) inherit from `Base`.
- API endpoints or services use `SessionLocal()` to create a database session, perform operations, and then close the session.

```python
# Example of how to use SessionLocal in an API endpoint (FastAPI context)
from sqlalchemy.orm import Session
from packages.database.config import SessionLocal, Base, engine

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Example of defining a model
from sqlalchemy import Column, Integer, String

class MyModel(Base):
    __tablename__ = "my_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

# To create tables (usually done via migrations, but for initial setup/testing)
# Base.metadata.create_all(bind=engine)
```