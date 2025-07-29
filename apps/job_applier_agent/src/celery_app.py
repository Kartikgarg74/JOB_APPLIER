from celery import Celery
from dotenv import load_dotenv
load_dotenv()

from packages.config.settings import settings

celery_app = Celery(
    "job_applier_agent",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["apps.job_applier_agent.src.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

if __name__ == "__main__":
    celery_app.start()
