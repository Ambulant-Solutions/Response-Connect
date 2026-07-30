from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.blueprints.jobs.models import Job


JobHandler = Callable[[Job], Any]

_handlers: dict[str, JobHandler] = {}


def register_handler(job_type: str):
    """Register a function as the handler for a particular job type."""

    def decorator(function: JobHandler) -> JobHandler:
        if job_type in _handlers:
            raise ValueError(
                f"A handler is already registered for job type '{job_type}'."
            )

        _handlers[job_type] = function
        return function

    return decorator


def get_handler(job_type: str) -> JobHandler | None:
    """Return the registered handler for a job type."""
    return _handlers.get(job_type)