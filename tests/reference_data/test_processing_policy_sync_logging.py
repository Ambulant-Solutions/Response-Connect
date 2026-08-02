import logging

from app.files import (
    get_file_processing_policy_synchroniser,
)


def test_processing_policy_sync_emits_summary_log(
    app,
    caplog,
) -> None:
    with app.app_context():
        synchroniser = (
            get_file_processing_policy_synchroniser()
        )

        with caplog.at_level(
            logging.INFO,
            logger=(
                "app.files.processing_policies"
            ),
        ):
            result = synchroniser.synchronise(
                dry_run=True
            )

        matching_records = [
            record
            for record in caplog.records
            if getattr(
                record,
                "platform_event",
                None,
            )
            == "reference_data.synchronised"
        ]

        assert len(matching_records) == 1

        record = matching_records[0]

        assert record.dataset == (
            "files.processing_policies"
        )
        assert record.dry_run is True
        assert record.created_count == (
            result.created_count
        )
        assert record.updated_count == (
            result.updated_count
        )
        assert record.unchanged_count == (
            result.unchanged_count
        )
        assert record.conflict_count == (
            result.conflict_count
        )