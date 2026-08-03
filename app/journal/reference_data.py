"""System-owned reference vocabulary for the Event Journal."""

from __future__ import annotations

from app.reference_data import (
    ReferenceDatasetDefinition,
    ReferenceRecordDefinition,
)


JOURNAL_CLASSIFICATION_DATASET = (
    ReferenceDatasetDefinition(
        name="journal.classifications",
        records=(
            ReferenceRecordDefinition(
                code="operational",
                values={
                    "name": "Operational",
                    "description": (
                        "Operational activity and "
                        "day-to-day service delivery."
                    ),
                    "sort_order": 10,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "description",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="audit",
                values={
                    "name": "Audit",
                    "description": (
                        "Activity requiring historical "
                        "accountability or traceability."
                    ),
                    "sort_order": 20,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "description",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="security",
                values={
                    "name": "Security",
                    "description": (
                        "Authentication, access, and "
                        "security-related activity."
                    ),
                    "sort_order": 30,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "description",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="system",
                values={
                    "name": "System",
                    "description": (
                        "Significant automated or "
                        "platform-generated activity."
                    ),
                    "sort_order": 40,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "description",
                    "sort_order",
                }),
            ),
        ),
    )
)


JOURNAL_SOURCE_DATASET = ReferenceDatasetDefinition(
    name="journal.sources",
    records=(
        ReferenceRecordDefinition(
            code="web",
            values={
                "name": "Web",
                "sort_order": 10,
                "is_active": True,
            },
            system_owned_fields=frozenset({
                "name",
                "sort_order",
            }),
        ),
        ReferenceRecordDefinition(
            code="api",
            values={
                "name": "API",
                "sort_order": 20,
                "is_active": True,
            },
            system_owned_fields=frozenset({
                "name",
                "sort_order",
            }),
        ),
        ReferenceRecordDefinition(
            code="worker",
            values={
                "name": "Background Worker",
                "sort_order": 30,
                "is_active": True,
            },
            system_owned_fields=frozenset({
                "name",
                "sort_order",
            }),
        ),
        ReferenceRecordDefinition(
            code="scheduler",
            values={
                "name": "Scheduler",
                "sort_order": 40,
                "is_active": True,
            },
            system_owned_fields=frozenset({
                "name",
                "sort_order",
            }),
        ),
        ReferenceRecordDefinition(
            code="integration",
            values={
                "name": "Integration",
                "sort_order": 50,
                "is_active": True,
            },
            system_owned_fields=frozenset({
                "name",
                "sort_order",
            }),
        ),
        ReferenceRecordDefinition(
            code="system",
            values={
                "name": "System",
                "sort_order": 60,
                "is_active": True,
            },
            system_owned_fields=frozenset({
                "name",
                "sort_order",
            }),
        ),
        ReferenceRecordDefinition(
            code="import",
            values={
                "name": "Import",
                "sort_order": 70,
                "is_active": True,
            },
            system_owned_fields=frozenset({
                "name",
                "sort_order",
            }),
        ),
    ),
)


JOURNAL_SEVERITY_DATASET = (
    ReferenceDatasetDefinition(
        name="journal.severities",
        records=(
            ReferenceRecordDefinition(
                code="information",
                values={
                    "name": "Information",
                    "sort_order": 10,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="warning",
                values={
                    "name": "Warning",
                    "sort_order": 20,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="critical",
                values={
                    "name": "Critical",
                    "sort_order": 30,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
        ),
    )
)


JOURNAL_VISIBILITY_DATASET = (
    ReferenceDatasetDefinition(
        name="journal.visibilities",
        records=(
            ReferenceRecordDefinition(
                code="standard",
                values={
                    "name": "Standard",
                    "sort_order": 10,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="restricted",
                values={
                    "name": "Restricted",
                    "sort_order": 20,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="confidential",
                values={
                    "name": "Confidential",
                    "sort_order": 30,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="security",
                values={
                    "name": "Security",
                    "sort_order": 40,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
            ReferenceRecordDefinition(
                code="clinical",
                values={
                    "name": "Clinical",
                    "sort_order": 50,
                    "is_active": True,
                },
                system_owned_fields=frozenset({
                    "name",
                    "sort_order",
                }),
            ),
        ),
    )
)


JOURNAL_REFERENCE_DATASETS = (
    JOURNAL_CLASSIFICATION_DATASET,
    JOURNAL_SOURCE_DATASET,
    JOURNAL_SEVERITY_DATASET,
    JOURNAL_VISIBILITY_DATASET,
)


__all__ = [
    "JOURNAL_CLASSIFICATION_DATASET",
    "JOURNAL_REFERENCE_DATASETS",
    "JOURNAL_SEVERITY_DATASET",
    "JOURNAL_SOURCE_DATASET",
    "JOURNAL_VISIBILITY_DATASET",
]