import pytest

from sqlalchemy import delete

from app import create_app
from app.extensions import db
from app.desks.models import Desk
from app.files.models import FileProcessingPolicy
from app.journal.models import JournalEntry


def _remove_test_processing_policies() -> None:
    db.session.rollback()

    db.session.execute(
        delete(FileProcessingPolicy).where(
            FileProcessingPolicy.code.like("test_%")
        )
    )

    db.session.commit()

def _remove_test_desks() -> None:
    """Remove all test Desks from the bottom of the hierarchy upward."""

    db.session.rollback()

    while True:
        test_desks = (
            db.session.query(Desk)
            .filter(
                Desk.code.in_(
                    [
                        "organisation",
                        "company",
                        "second_root",
                        "invalid_root",
                        "operations",
                        "patient_transport",
                        "devon_pts",
                        "fleet",
                        "resources",
                        "training",
                        "active",
                        "inactive",
                        "orphan",
                        "archived",
                    ]
                )
            )
            .all()
        )

        if not test_desks:
            break

        test_ids = {
            desk.id
            for desk in test_desks
        }

        parent_ids = {
            desk.parent_id
            for desk in test_desks
            if desk.parent_id is not None
        }

        leaf_desks = [
            desk
            for desk in test_desks
            if desk.id not in parent_ids
        ]

        if not leaf_desks:
            raise RuntimeError(
                "Test Desk cleanup could not find "
                "a leaf Desk. The test hierarchy may "
                "contain a cycle."
            )

        for desk in leaf_desks:
            db.session.delete(desk)

        db.session.flush()

    db.session.commit()

def _remove_test_journal_entries() -> None:
    db.session.rollback()

    db.session.execute(
        delete(JournalEntry).where(
            JournalEntry.event_code.like(
                "system.test_%"
            )
            | (
                JournalEntry.event_code
                == "desk.created"
            )
        )
    )

    db.session.commit()


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.app_context():
        # Remove leftovers from interrupted or failed earlier runs.
        _remove_test_journal_entries()
        _remove_test_desks()
        _remove_test_processing_policies()

        yield app

        _remove_test_journal_entries()
        _remove_test_desks()
        _remove_test_processing_policies()
        db.session.remove()