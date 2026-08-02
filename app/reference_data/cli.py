from __future__ import annotations

import click
from flask import Flask

from app.reference_data import (
    ReferenceDataChangeType,
    get_reference_data_registry,
)

import logging

from app.platform_logging import log_platform_event


logger = logging.getLogger(__name__)


def register_reference_data_cli(
    app: Flask,
) -> None:
    @app.cli.group("reference-data")
    def reference_data_group() -> None:
        """Manage system reference data."""

    @reference_data_group.command("list")
    def list_datasets() -> None:
        registry = get_reference_data_registry()

        for dataset_name in registry.list_names():
            click.echo(dataset_name)

    @reference_data_group.command("sync")
    @click.option(
        "--dataset",
        "dataset_name",
        default=None,
        help="Synchronise only one named dataset.",
    )
    @click.option(
        "--dry-run",
        is_flag=True,
        help="Show changes without committing them.",
    )
    def sync_reference_data(
        dataset_name: str | None,
        dry_run: bool,
    ) -> None:
        registry = get_reference_data_registry()

        synchronisers = (
            [registry.get(dataset_name)]
            if dataset_name
            else list(
                registry.iter_synchronisers()
            )
        )

        for synchroniser in synchronisers:
            result = synchroniser.synchronise(
                dry_run=dry_run
            )

            click.echo(
                f"{result.dataset}: "
                f"{result.created_count} created, "
                f"{result.updated_count} updated, "
                f"{result.unchanged_count} unchanged, "
                f"{result.conflict_count} conflicts"
            )

            log_platform_event(
                logger,
                "reference_data.cli_sync_completed",
                fields={
                    "dataset": result.dataset,
                    "dry_run": dry_run,
                    "created_count": (
                        result.created_count
                    ),
                    "updated_count": (
                        result.updated_count
                    ),
                    "unchanged_count": (
                        result.unchanged_count
                    ),
                    "conflict_count": (
                        result.conflict_count
                    ),
                },
            )

            for change in result.changes:
                prefix = {
                    ReferenceDataChangeType.CREATE: "+",
                    ReferenceDataChangeType.UPDATE: "~",
                    ReferenceDataChangeType.UNCHANGED: "=",
                    ReferenceDataChangeType.CONFLICT: "!",
                }[change.change_type]

                details = ""

                if change.changed_fields:
                    details = (
                        " ["
                        + ", ".join(
                            change.changed_fields
                        )
                        + "]"
                    )

                click.echo(
                    f"  {prefix} {change.code}"
                    f"{details}"
                )