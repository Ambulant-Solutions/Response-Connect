import pytest

from sqlalchemy import delete

from app import create_app
from app.extensions import db
from app.desks.models import Desk
from app.files.models import FileProcessingPolicy
from app.journal.models import (
    JournalEntry,
    JournalReference,
)

def _remove_test_processing_policies() -> None:
    db.session.rollback()

    db.session.execute(
        delete(FileProcessingPolicy).where(
            FileProcessingPolicy.code.like("test_%")
        )
    )

    db.session.commit()

def _remove_test_desks() -> None:
    """Delete all test Desks from leaves to root."""

    db.session.rollback()

    while True:
        test_desks = (
            db.session.query(Desk)
            .filter(
                Desk.code.like("test_%")
            )
            .all()
        )

        if not test_desks:
            break

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
                "Test Desk cleanup could not find a "
                "leaf Desk. The test hierarchy may "
                "contain a cycle."
            )

        for desk in leaf_desks:
            db.session.delete(desk)

        db.session.flush()

    db.session.commit()

def _remove_test_journal_entries() -> None:
    """Remove all Journal Entries before referenced records."""

    db.session.rollback()

    db.session.execute(
        delete(JournalEntry)
    )

    db.session.commit()


def _remove_test_journal_references() -> None:
    """Remove all Journal References after Journal Entries."""

    db.session.rollback()

    db.session.execute(
        delete(JournalReference)
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
        _remove_test_journal_references()
        _remove_test_desks()
        _remove_test_processing_policies()

        yield app

        _remove_test_journal_entries()
        _remove_test_journal_references()
        _remove_test_desks()
        _remove_test_processing_policies()
        db.session.remove()