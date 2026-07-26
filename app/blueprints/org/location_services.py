from app.blueprints.org.models import (
    LocationUse,
    OrganisationLocation,
)


class InvalidLocationUse(ValueError):
    pass


def require_location_use(
    location: OrganisationLocation,
    required_use: str | LocationUse,
) -> None:
    use_code = (
        required_use.value
        if isinstance(required_use, LocationUse)
        else required_use
    )

    if not location.is_active:
        raise InvalidLocationUse(
            f"{location.name} is not an active location."
        )

    if not location.permits(use_code):
        raise InvalidLocationUse(
            f"{location.name} cannot be used for {use_code}."
        )