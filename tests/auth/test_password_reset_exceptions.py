import pytest
from flask import Flask

from app.blueprints.auth.password_reset import (
    PasswordResetTokenError,
    _get_max_age,
    _get_serializer,
)
from app.exceptions import (
    ConfigurationError,
    ResponseConnectError,
    ValidationError,
)


def create_test_app(
    **configuration,
) -> Flask:
    app = Flask(__name__)
    app.config.update(configuration)
    return app


def test_password_reset_token_error_uses_platform_hierarchy(
) -> None:
    assert issubclass(
        PasswordResetTokenError,
        ValidationError,
    )
    assert issubclass(
        PasswordResetTokenError,
        ResponseConnectError,
    )


def test_password_reset_token_error_preserves_message(
) -> None:
    error = PasswordResetTokenError(
        "The password-reset token is invalid."
    )

    assert str(error) == (
        "The password-reset token is invalid."
    )


def test_serializer_requires_secret_key() -> None:
    app = create_test_app(
        SECRET_KEY=None,
    )

    with app.app_context():
        with pytest.raises(
            ConfigurationError,
            match=(
                "SECRET_KEY must be configured"
            ),
        ):
            _get_serializer()


def test_serializer_accepts_configured_secret_key(
) -> None:
    app = create_test_app(
        SECRET_KEY="test-secret-key",
    )

    with app.app_context():
        serializer = _get_serializer()

    assert serializer is not None


@pytest.mark.parametrize(
    "configured_value",
    [
        None,
        "",
        "not-an-integer",
        object(),
    ],
)
def test_password_reset_max_age_rejects_invalid_values(
    configured_value,
) -> None:
    app = create_test_app(
        PASSWORD_RESET_TOKEN_MAX_AGE=(
            configured_value
        ),
    )

    with app.app_context():
        with pytest.raises(
            ConfigurationError,
            match=(
                "PASSWORD_RESET_TOKEN_MAX_AGE "
                "must be a valid integer"
            ),
        ):
            _get_max_age()


@pytest.mark.parametrize(
    "configured_value",
    [
        0,
        -1,
        "-60",
    ],
)
def test_password_reset_max_age_must_be_positive(
    configured_value,
) -> None:
    app = create_test_app(
        PASSWORD_RESET_TOKEN_MAX_AGE=(
            configured_value
        ),
    )

    with app.app_context():
        with pytest.raises(
            ConfigurationError,
            match=(
                "PASSWORD_RESET_TOKEN_MAX_AGE "
                "must be greater than zero"
            ),
        ):
            _get_max_age()


@pytest.mark.parametrize(
    ("configured_value", "expected"),
    [
        (3600, 3600),
        ("7200", 7200),
        (60.0, 60),
    ],
)
def test_password_reset_max_age_accepts_valid_values(
    configured_value,
    expected,
) -> None:
    app = create_test_app(
        PASSWORD_RESET_TOKEN_MAX_AGE=(
            configured_value
        ),
    )

    with app.app_context():
        result = _get_max_age()

    assert result == expected