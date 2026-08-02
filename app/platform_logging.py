from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any


_PLATFORM_FIELD = "platform_event"


def log_platform_event(
    logger: logging.Logger,
    event: str,
    *,
    level: int = logging.INFO,
    message: str | None = None,
    fields: Mapping[str, Any] | None = None,
) -> None:
    """
    Emit a structured platform log event.

    The default formatter may only display the message, but structured logging
    handlers can inspect `platform_event` and the additional fields.
    """

    extra: dict[str, Any] = {
        _PLATFORM_FIELD: event,
    }

    if fields:
        extra.update(fields)

    logger.log(
        level,
        message or event,
        extra=extra,
    )