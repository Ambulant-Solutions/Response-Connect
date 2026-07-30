import uuid

from flask import current_app

from app.extensions import db
from app.blueprints.jobs.models import Job
from app.blueprints.jobs.tasks import execute_job


def create_job(
    job_type: str,
    payload: dict | None = None,
    created_by_id: uuid.UUID | None = None,
    scheduled_at=None,
    priority: int = 5,
) -> Job:

    job = Job(
        type=job_type,
        payload=payload,
        created_by_id=created_by_id,
        scheduled_at=scheduled_at,
        priority=priority,
    )

    db.session.add(job)
    db.session.commit()

    return job


def queue_job(job: Job):

    task = execute_job.delay(str(job.id))

    job.celery_task_id = task.id

    db.session.commit()

    return job