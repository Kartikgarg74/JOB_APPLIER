# Message Queue Module Requirements (`requirements.txt`)

## Purpose
This `requirements.txt` file specifies the Python dependencies required for the `packages/message_queue` module to function correctly. These packages are essential for setting up and running the Celery asynchronous task queue.

## Dependencies

- **`celery==5.3.6`**
  - **Purpose**: The core distributed task queue framework used for asynchronous processing in the application.
  - **Version**: `5.3.6` ensures compatibility and stability with the current application setup.

- **`redis==5.0.1`**
  - **Purpose**: A Python client for Redis, which is commonly used as both a message broker and a result backend for Celery. It facilitates the communication between the Celery application and its workers, and stores the results of executed tasks.
  - **Version**: `5.0.1` ensures compatibility with the Redis server and provides necessary functionalities for Celery's operations.

## Installation
To install these dependencies, navigate to the root of your project or the specific module directory (if managing dependencies per module) and use `pip`:

```bash
pip install -r packages/message_queue/requirements.txt
```

## Usage
These dependencies are crucial for running the Celery worker and for any part of the application that interacts with the message queue, such as defining tasks or sending tasks for asynchronous execution. Ensure these are installed in your development and deployment environments where Celery is utilized.