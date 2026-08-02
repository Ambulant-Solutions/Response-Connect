import pytest

from sqlalchemy import delete

from app import create_app
from app.extensions import db
from app.desks.models import Desk
from app.files.models import FileProcessingPolicy


def _remove_test_processing_policies() -> None:
    db.session.rollback()

    db.session.execute(
        delete(FileProcessingPolicy).where(
            FileProcessingPolicy.code.like("test_%")
        )
    )

    db.session.commit()

def _remove_test_desks() -> None:
    db.session.rollback()

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
                    "orphan",
                ]
            )
        )
        .all()
    )

    # Delete children before parents because parent deletion is restricted.
    for desk in reversed(test_desks):
        db.session.delete(desk)

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
        _remove_test_desks()
        _remove_test_processing_policies()

        yield app

        _remove_test_desks()
        _remove_test_processing_policies()
        db.session.remove()