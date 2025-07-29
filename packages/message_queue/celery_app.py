from celery import Celery
from kombu import Queue, Exchange, Connection
import os
from prometheus_client import Gauge


REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL", "redis://localhost:6379/0")
REDIS_TOKEN = os.getenv("UPSTASH_REDIS_REST_TOKEN", None)

# Prometheus Metrics for Celery Queue Depth
queue_depth_gauge = Gauge('celery_queue_depth', 'Current depth of Celery queues', ['queue_name'])


celery_app = Celery(
    "job_applier",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

# Dead letter queue setup
celery_app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
    Queue("dead_letter", Exchange("dead_letter"), routing_key="dead_letter"),
)
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"

# Rate limiting, retry, and prioritization
celery_app.conf.task_annotations = {
    "*": {"rate_limit": "10/m", "max_retries": 5, "default_retry_delay": 60},
}

# Monitoring (Flower):
# Run: flower -A packages.message_queue.celery_app --port=5555

# Example task with retry and priority
@celery_app.task(bind=True, default_retry_delay=30, max_retries=3, acks_late=True, queue="default")
def example_task(self, x, y):
    try:
        return x + y
    except Exception as exc:
        raise self.retry(exc=exc)

# Dead letter handler
@celery_app.task(queue="dead_letter")
def handle_dead_letter(task_name, args, kwargs, reason):
    print(f"Dead letter: {task_name} {args} {kwargs} Reason: {reason}")

# Periodic task (job scheduling)
from celery.schedules import crontab

@celery_app.task
def update_queue_depths():
    with Connection(celery_app.broker_url) as conn:
        with conn.channel() as channel:
            for queue_name in [q.name for q in celery_app.conf.task_queues]:
                try:
                    queue = conn.SimpleQueue(queue_name)
                    length = queue.qsize()
                    queue_depth_gauge.labels(queue_name).set(length)
                    queue.close()
                except Exception as e:
                    print(f"Error getting queue depth for {queue_name}: {e}")

celery_app.conf.beat_schedule = {
    "cleanup-old-files": {
        "task": "packages.utilities.file_management.file_cleanup.cleanup_old_file_versions",
        "schedule": crontab(hour=3, minute=0),
    },
    "update-celery-queue-depths": {
        "task": "packages.message_queue.celery_app.update_queue_depths",
        "schedule": crontab(minute='*/1'), # Run every minute
    },
}
