# Celery Application Configuration (`celery_app.py`)

## Purpose
This module (`celery_app.py`) is responsible for configuring and initializing the Celery application. Celery is used for asynchronous task processing, allowing long-running operations (e.g., job application submissions, data processing) to be offloaded from the main application thread, improving responsiveness and scalability.

## Dependencies
- `celery.Celery`: The core Celery library for creating an application instance.
- `packages.config.settings.settings`: Imports application settings, specifically for retrieving Celery broker and result backend URLs.

## Key Components

### `celery_app` Instance
- **Purpose**: The main Celery application instance.
- **Initialization Parameters**:
  - `"job_applier_agent"`: The name of the Celery application.
  - `broker=settings.CELERY_BROKER_URL`: The URL for the message broker (e.g., Redis, RabbitMQ) that Celery uses to send and receive messages.
  - `backend=settings.CELERY_RESULT_BACKEND`: The URL for the result backend where task results are stored.
  - `include=["packages.message_queue.tasks"]`: Specifies the modules where Celery should look for tasks. This ensures that tasks defined in `tasks.py` are registered with the Celery app.

### `celery_app.conf.update()`
- **Purpose**: Configures various settings for the Celery application.
- **Key Configuration Options**:
  - `task_track_started=True`: Enables tracking of task status, allowing the application to know when a task has started execution.
  - `task_acks_late=True`: Tasks are acknowledged after they have been executed, not before. This helps prevent data loss if a worker crashes during task execution.
  - `worker_prefetch_multiplier=1`: Configures how many tasks a worker can prefetch. A value of 1 means the worker will only prefetch one task at a time, ensuring fair distribution among workers.
  - `task_serializer="json"`: Specifies that tasks should be serialized using JSON.
  - `result_serializer="json"`: Specifies that task results should be serialized using JSON.
  - `accept_content=["json"]`: Defines the content types that Celery will accept.
  - `timezone="UTC"`: Sets the timezone for Celery to Coordinated Universal Time.
  - `enable_utc=True`: Ensures that timezone information is handled using UTC.

## Workflow
1.  The `Celery` instance is created, linking it to the message broker and result backend defined in the application settings.
2.  The `include` parameter ensures that tasks defined in `packages.message_queue.tasks` are automatically discovered and registered with this Celery application.
3.  Various configuration options are applied to control task behavior, serialization, and timezone handling.
4.  When this module is run directly (e.g., `python celery_app.py`), it starts the Celery worker, which begins listening for and executing tasks.

## Usage
This module is typically imported by other parts of the application that need to define or call Celery tasks. It is also the entry point for starting a Celery worker process.

### Example: Starting a Celery Worker
To start a Celery worker, you would typically run a command like:

```bash
celery -A packages.message_queue.celery_app worker -l info
```

Or, if running the file directly for development/testing:

```bash
python packages/message_queue/celery_app.py
```

### Example: Importing and Using in `tasks.py`
```python
# packages/message_queue/tasks.py
from packages.message_queue.celery_app import celery_app

@celery_app.task
def my_background_task(arg1, arg2):
    # Task logic here
    print(f"Executing task with {arg1} and {arg2}")
    return arg1 + arg2

# To call the task from another part of the application:
# from packages.message_queue.tasks import my_background_task
# my_background_task.delay(10, 20) # Asynchronously execute the task
```

## Configuration
Ensure that `settings.CELERY_BROKER_URL` and `settings.CELERY_RESULT_BACKEND` are correctly configured in `packages/config/settings.py` or via environment variables for Celery to function properly.