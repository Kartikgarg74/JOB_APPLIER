# Alembic Environment Configuration (`env.py`)

## Purpose
This `env.py` file is the core configuration script for Alembic migrations. It defines how Alembic interacts with the SQLAlchemy engine and models to generate and apply database migrations. It sets up the environment for both "offline" (script-only) and "online" (database-connected) migration modes.

## Dependencies
- `os`, `sys`: For path manipulation to ensure proper imports.
- `logging.config.fileConfig`: For configuring logging based on the Alembic ini file.
- `sqlalchemy.engine_from_config`, `sqlalchemy.pool`: For creating and managing database connections.
- `alembic.context`: The main interface for Alembic operations within the script.
- `packages.database.config.Base`: Imports the declarative base from the application's database configuration, which contains the metadata of all SQLAlchemy models.
- `packages.database.models`: Explicitly imports all defined SQLAlchemy models (`User`, `Education`, `Experience`, `Project`, `JobPreference`, etc.) to ensure their metadata is loaded and available for Alembic's autogenerate feature.

## Key Components

### `config`
- An `alembic.context.Config` object that provides access to values defined in the `alembic.ini` file.

### `target_metadata`
- Set to `Base.metadata`, which is the collection of all SQLAlchemy table definitions. This is essential for Alembic's `autogenerate` feature to detect schema changes.

### `run_migrations_offline()`
- **Purpose**: Configures the migration context for "offline" mode. In this mode, Alembic generates SQL scripts without connecting to a database. It's useful for reviewing SQL changes before applying them.
- **Workflow**: Retrieves the database URL from the configuration and configures the context with `literal_binds=True` and `dialect_opts` for named parameters.

### `run_migrations_online()`
- **Purpose**: Configures the migration context for "online" mode. In this mode, Alembic connects to the database and applies migrations directly.
- **Workflow**: Creates a SQLAlchemy engine using `engine_from_config` based on the `alembic.ini` settings, establishes a connection, and then configures the Alembic context with this connection.

### Main Execution Block
- Uses `context.is_offline_mode()` to determine whether to run migrations in offline or online mode, calling the appropriate function.

## Workflow
1. **Path Setup**: Adjusts `sys.path` to allow importing modules from the project root, specifically `packages.database.config` and `packages.database.models`.
2. **Logging Configuration**: Initializes logging based on the `alembic.ini` file.
3. **Metadata Loading**: Imports all necessary SQLAlchemy models to ensure their metadata is loaded into `Base.metadata`, which Alembic uses to compare the current database schema with the model definitions.
4. **Mode Detection**: Alembic determines whether to run in offline or online mode based on command-line arguments or configuration.
5. **Context Configuration**: The appropriate `run_migrations_offline` or `run_migrations_online` function is called to configure the Alembic context with the database URL or an active connection and the `target_metadata`.
6. **Migration Execution**: `context.run_migrations()` is called within a transaction (`context.begin_transaction()`) to execute the migration scripts.

## Usage
This file is not typically run directly by the user. It is invoked by the `alembic` command-line tool (e.g., `alembic upgrade head`, `alembic revision --autogenerate`). Its primary role is to provide the necessary environment for Alembic to perform its operations.

## Security Considerations
- Ensure that database connection strings (especially in `alembic.ini` or environment variables) are handled securely and not exposed in version control.
- The `sys.path` modification should be carefully managed to prevent unintended module imports or security vulnerabilities.