import pytest

from sqlalchemy import delete

from app import create_app
from app.extensions import db
from app.files.models import FileProcessingPolicy


def _remove_test_processing_policies() -> None:
    db.session.rollback()

    db.session.execute(
        delete(FileProcessingPolicy).where(
            FileProcessingPolicy.code.like("test_%")
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
        _remove_test_processing_policies()

        yield app

        _remove_test_processing_policies()
        db.session.remove()