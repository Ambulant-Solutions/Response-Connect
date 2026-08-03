"""Tests for Event Journal Reference Data definitions."""

from app.journal.reference_data import (
    JOURNAL_CLASSIFICATION_DATASET,
    JOURNAL_REFERENCE_DATASETS,
    JOURNAL_SEVERITY_DATASET,
    JOURNAL_SOURCE_DATASET,
    JOURNAL_VISIBILITY_DATASET,
)


def record_codes(dataset) -> set[str]:
    return {
        record.code
        for record in dataset.records
    }


def test_journal_reference_dataset_names() -> None:
    assert {
        dataset.name
        for dataset in JOURNAL_REFERENCE_DATASETS
    } == {
        "journal.classifications",
        "journal.severities",
        "journal.sources",
        "journal.visibilities",
    }


def test_journal_classification_codes() -> None:
    assert record_codes(
        JOURNAL_CLASSIFICATION_DATASET
    ) == {
        "operational",
        "audit",
        "security",
        "system",
    }


def test_journal_source_codes() -> None:
    assert record_codes(
        JOURNAL_SOURCE_DATASET
    ) == {
        "web",
        "api",
        "worker",
        "scheduler",
        "integration",
        "system",
        "import",
    }


def test_journal_severity_codes() -> None:
    assert record_codes(
        JOURNAL_SEVERITY_DATASET
    ) == {
        "information",
        "warning",
        "critical",
    }


def test_journal_visibility_codes() -> None:
    assert record_codes(
        JOURNAL_VISIBILITY_DATASET
    ) == {
        "standard",
        "restricted",
        "confidential",
        "security",
        "clinical",
    }