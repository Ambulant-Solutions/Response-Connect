from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.blueprints.jobs.models import Job, JobStatus
from app.blueprints.jobs.tasks import execute_job
from app.extensions import db


def create_job(
    job_type: str,
    payload: dict | None = None,
    created_by_id: uuid.UUID | None = None,
    scheduled_at: datetime | None = None,
    priority: int = 5,
) -> Job:
    """Create and persist a new job without queuing it."""

    job = Job(
        type=job_type,
        payload=payload,
        created_by_id=created_by_id,
        scheduled_at=scheduled_at,
        priority=priority,
        status=JobStatus.PENDING,
    )

    db.session.add(job)
    db.session.commit()

    return job


def queue_job(job: Job) -> Job:
    """Send an existing job to Celery for immediate execution."""

    if job.status == JobStatus.CANCELLED:
        raise ValueError("A cancelled job cannot be queued.")

    if job.status == JobStatus.COMPLETED:
        raise ValueError("A completed job cannot be queued again.")

    if job.status == JobStatus.RUNNING:
        raise ValueError("A running job cannot be queued again.")

    task = execute_job.delay(str(job.id))

    job.celery_task_id = task.id
    job.status = JobStatus.QUEUED
    job.scheduled_at = None

    db.session.commit()

    return job


def create_and_queue_job(
    job_type: str,
    payload: dict | None = None,
    created_by_id: uuid.UUID | None = None,
    priority: int = 5,
) -> Job:
    """Create a job and immediately queue it for execution."""

    job = create_job(
        job_type=job_type,
        payload=payload,
        created_by_id=created_by_id,
        priority=priority,
    )

    return queue_job(job)


def schedule_job(job: Job) -> Job:
    """Queue a job for execution at its scheduled time."""

    if job.scheduled_at is None:
        raise ValueError("The job does not have a scheduled time.")

    scheduled_at = job.scheduled_at

    if scheduled_at.tzinfo is None:
        scheduled_at = scheduled_at.replace(tzinfo=timezone.utc)

    if scheduled_at <= datetime.now(timezone.utc):
        raise ValueError("The scheduled time must be in the future.")

    if job.status == JobStatus.CANCELLED:
        raise ValueError("A cancelled job cannot be scheduled.")

    if job.status == JobStatus.COMPLETED:
        raise ValueError("A completed job cannot be scheduled again.")

    if job.status == JobStatus.RUNNING:
        raise ValueError("A running job cannot be scheduled.")

    task = execute_job.apply_async(
        args=[str(job.id)],
        eta=scheduled_at,
    )

    job.celery_task_id = task.id
    job.status = JobStatus.QUEUED

    db.session.commit()

    return job