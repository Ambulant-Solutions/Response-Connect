from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any

from app.celery import celery
from app.extensions import db
from app.blueprints.jobs.models import Job, JobStatus
from app.blueprints.jobs.registry import get_handler

logger = logging.getLogger(__name__)


class JobNotFoundError(Exception):
    """Raised when a queued job no longer exists."""


class JobHandlerNotFoundError(Exception):
    """Raised when no handler is registered for a job type."""


@celery.task(
    bind=True,
    name="app.blueprints.jobs.tasks.execute_job",
    max_retries=3,
)
def execute_job(self, job_id: str) -> dict[str, Any]:
    """
    Execute a database-backed background job.

    The PostgreSQL Job record is the permanent source of truth. Celery and
    Redis are responsible only for delivering and executing the work.

    Args:
        job_id:
            UUID of the Job record, passed as a string so it can be safely
            serialised by Celery.

    Returns:
        A small serialisable result describing the completed job.

    Raises:
        JobNotFoundError:
            If the supplied job UUID does not exist.
        JobHandlerNotFoundError:
            If no handler has been registered for the job type.
        Exception:
            Re-raised after the Job record has been marked as failed.
    """
    job_uuid = _parse_job_id(job_id)
    job = db.session.get(Job, job_uuid)

    if job is None:
        logger.error("Job %s does not exist.", job_id)
        raise JobNotFoundError(f"Job {job_id} does not exist.")

    # Do not execute a job that has been cancelled before the worker receives it.
    if job.status == JobStatus.CANCELLED:
        logger.info("Job %s was cancelled before execution.", job.id)

        return {
            "job_id": str(job.id),
            "status": job.status,
            "message": "Job was cancelled before execution.",
        }

    # Avoid accidentally executing an already completed job again.
    if job.status == JobStatus.COMPLETED:
        logger.warning("Job %s has already completed.", job.id)

        return {
            "job_id": str(job.id),
            "status": job.status,
            "message": "Job has already completed.",
        }

    _mark_job_running(job, celery_task_id=self.request.id)

    try:
        handler = get_handler(job.type)

        if handler is None:
            raise JobHandlerNotFoundError(
                f"No handler is registered for job type '{job.type}'."
            )

        logger.info(
            "Executing job %s of type %s, attempt %s.",
            job.id,
            job.type,
            job.attempts,
        )

        # Handlers receive the complete Job object. They can inspect the
        # payload and update domain-specific records as required.
        result = handler(job)

        # Refresh the job in case the handler changed it in another transaction.
        db.session.refresh(job)

        # A running handler may cancel the job deliberately.
        if job.status == JobStatus.CANCELLED:
            logger.info("Job %s was cancelled during execution.", job.id)

            return {
                "job_id": str(job.id),
                "status": job.status,
                "result": _serialise_result(result),
            }

        _mark_job_completed(job)

        logger.info("Job %s completed successfully.", job.id)

        return {
            "job_id": str(job.id),
            "status": job.status,
            "result": _serialise_result(result),
        }

    except Exception as exc:
        # Roll back any failed transaction left open by the handler before
        # attempting to update the Job record.
        db.session.rollback()

        job = db.session.get(Job, job_uuid)

        if job is not None:
            _mark_job_failed(job, exc)

        logger.exception(
            "Job %s of type %s failed on attempt %s.",
            job_id,
            job.type if job is not None else "UNKNOWN",
            job.attempts if job is not None else "UNKNOWN",
        )

        # The Job record tracks each actual worker execution. Retry only while
        # the configured Celery retry limit has not been reached.
        if self.request.retries < self.max_retries:
            countdown = _retry_countdown(self.request.retries)

            logger.info(
                "Retrying job %s in %s seconds.",
                job_id,
                countdown,
            )

            raise self.retry(
                exc=exc,
                countdown=countdown,
            )

        raise

    finally:
        # Flask-SQLAlchemy normally cleans sessions at the end of an app
        # context, but removing it explicitly is safer for long-lived workers.
        db.session.remove()


def _parse_job_id(job_id: str) -> uuid.UUID:
    """Convert a serialised job ID into a UUID."""
    try:
        return uuid.UUID(str(job_id))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError(f"Invalid job UUID: {job_id!r}") from exc


def _mark_job_running(job: Job, celery_task_id: str | None) -> None:
    """Mark a job as running and record the current execution attempt."""
    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow()
    job.completed_at = None
    job.error_message = None
    job.celery_task_id = celery_task_id
    job.attempts += 1

    db.session.commit()


def _mark_job_completed(job: Job) -> None:
    """Mark a job as successfully completed."""
    job.status = JobStatus.COMPLETED
    job.completed_at = datetime.utcnow()
    job.error_message = None

    db.session.commit()


def _mark_job_failed(job: Job, error: Exception) -> None:
    """Persist failure information against a job."""
    job.status = JobStatus.FAILED
    job.completed_at = datetime.utcnow()
    job.error_message = _format_error(error)

    db.session.commit()


def _format_error(error: Exception, maximum_length: int = 10_000) -> str:
    """
    Produce a bounded error message suitable for storing in the database.

    Full tracebacks remain available in the worker logs; the database stores
    a concise description for the administrative interface and audit trail.
    """
    message = f"{type(error).__name__}: {error}"

    if len(message) > maximum_length:
        return f"{message[:maximum_length]}…"

    return message


def _retry_countdown(current_retry: int) -> int:
    """
    Return an exponential retry delay.

    Celery's retry count is zero for the first retry request, producing:

        first retry:  30 seconds
        second retry: 60 seconds
        third retry:  120 seconds
    """
    return 30 * (2**current_retry)


def _serialise_result(result: Any) -> Any:
    """
    Return a Celery-result-safe representation.

    Job handlers should normally return JSON-serialisable values. This fallback
    prevents an otherwise successful job failing only because its return value
    cannot be encoded by the result backend.
    """
    if result is None or isinstance(result, (str, int, float, bool, list, dict)):
        return result

    if isinstance(result, uuid.UUID):
        return str(result)

    return str(result)