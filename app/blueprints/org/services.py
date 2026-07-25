from __future__ import annotations

from flask import abort, g
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from werkzeug.local import LocalProxy

from app.extensions import db
from app.blueprints.org.models import Organisation


_ORGANISATION_CONTEXT_KEY = "_response_connect_organisation"


def get_current_organisation() -> Organisation | None:
    """
    Return the active primary organisation for this installation.

    The result is cached on Flask's application context, so the database
    is queried at most once during a request or CLI command.
    """

    if not hasattr(g, _ORGANISATION_CONTEXT_KEY):
        statement = (
            select(Organisation)
            .where(
                Organisation.is_primary.is_(True),
                Organisation.is_active.is_(True),
            )
            .options(
                selectinload(Organisation.locations),
            )
        )

        organisation = db.session.execute(
            statement
        ).scalar_one_or_none()

        setattr(
            g,
            _ORGANISATION_CONTEXT_KEY,
            organisation,
        )

    return getattr(g, _ORGANISATION_CONTEXT_KEY)


def require_current_organisation() -> Organisation:
    """
    Return the current organisation or stop with a service-unavailable
    response if the installation has not yet been configured.
    """

    organisation = get_current_organisation()

    if organisation is None:
        abort(
            503,
            description=(
                "This Response Connect installation has not yet been "
                "configured with an organisation."
            ),
        )

    return organisation


def clear_current_organisation() -> None:
    """
    Clear the cached organisation for the current application context.

    Use this after replacing the primary organisation or changing which
    organisation is active.
    """

    g.pop(_ORGANISATION_CONTEXT_KEY, None)


current_organisation = LocalProxy(require_current_organisation)