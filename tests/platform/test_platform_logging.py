import logging

from app.platform_logging import (
    log_platform_event,
)


def test_log_platform_event_emits_structured_fields(
    caplog,
) -> None:
    logger = logging.getLogger(
        "tests.platform_logging"
    )

    with caplog.at_level(
        logging.INFO,
        logger=logger.name,
    ):
        log_platform_event(
            logger,
            "test.event",
            fields={
                "record_id": "123",
                "count": 4,
            },
        )

    assert len(caplog.records) == 1

    record = caplog.records[0]

    assert record.getMessage() == "test.event"
    assert record.platform_event == "test.event"
    assert record.record_id == "123"
    assert record.count == 4


def test_log_platform_event_supports_custom_message(
    caplog,
) -> None:
    logger = logging.getLogger(
        "tests.platform_logging.message"
    )

    with caplog.at_level(
        logging.WARNING,
        logger=logger.name,
    ):
        log_platform_event(
            logger,
            "test.warning",
            level=logging.WARNING,
            message="A test warning occurred.",
        )

    record = caplog.records[0]

    assert record.levelno == logging.WARNING
    assert record.getMessage() == (
        "A test warning occurred."
    )
    assert record.platform_event == "test.warning"