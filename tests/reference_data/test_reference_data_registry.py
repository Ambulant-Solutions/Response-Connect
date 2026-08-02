from flask import Flask
import pytest

from app.exceptions import ConfigurationError
from app.reference_data import (
    get_reference_data_registry,
)


def test_get_reference_data_registry_requires_initialisation(
) -> None:
    app = Flask(__name__)

    with app.app_context():
        with pytest.raises(
            ConfigurationError,
            match=(
                "The reference-data registry has not "
                "been initialised"
            ),
        ):
            get_reference_data_registry()