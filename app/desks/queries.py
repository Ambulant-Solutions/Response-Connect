"""Desk hierarchy and lookup queries."""

from __future__ import annotations

import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.desks.exceptions import (
    DeskNotFoundError,
    InvalidDeskError,
)
from app.desks.models import Desk
from app.desks.validators import validate_desk_code


class DeskQueryService:
    """Read-only queries for Desk records and immediate hierarchy data."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def get(
        self,
        desk_id: uuid.UUID,
    ) -> Desk:
        """Return a Desk or raise DeskNotFoundError."""

        desk = self.session.get(
            Desk,
            desk_id,
        )

        if desk is None:
            raise DeskNotFoundError(
                "The Desk could not be found."
            )

        return desk

    def find_by_code(
        self,
        code: str,
    ) -> Desk | None:
        """Return the Desk using a stable code, or None."""

        normalised_code = validate_desk_code(code)

        return self.session.scalar(
            select(Desk).where(
                Desk.code == normalised_code
            )
        )

    def get_by_code(
        self,
        code: str,
    ) -> Desk:
        """Return the Desk using a stable code or raise not found."""

        normalised_code = validate_desk_code(code)

        desk = self.session.scalar(
            select(Desk).where(
                Desk.code == normalised_code
            )
        )

        if desk is None:
            raise DeskNotFoundError(
                "No Desk exists with code "
                f"{normalised_code!r}."
            )

        return desk

    def exists(
        self,
        desk_id: uuid.UUID,
    ) -> bool:
        """Return whether a Desk exists."""

        return (
            self.session.scalar(
                select(Desk.id).where(
                    Desk.id == desk_id
                )
            )
            is not None
        )

    def list(
        self,
        *,
        active_only: bool = False,
    ) -> list[Desk]:
        """Return Desks ordered consistently for administration."""

        statement = self._base_list_query()

        if active_only:
            statement = statement.where(
                Desk.is_active.is_(True)
            )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def children(
        self,
        parent_id: uuid.UUID,
        *,
        active_only: bool = False,
    ) -> list[Desk]:
        """Return the immediate child Desks of a parent."""

        self.get(parent_id)

        statement = (
            select(Desk)
            .where(
                Desk.parent_id == parent_id
            )
            .order_by(
                Desk.name,
                Desk.code,
            )
        )

        if active_only:
            statement = statement.where(
                Desk.is_active.is_(True)
            )

        return list(
            self.session.scalars(
                statement
            ).all()
        )

    def path(
        self,
        desk_id: uuid.UUID,
    ) -> list[Desk]:
        """Return the hierarchy path from root to the requested Desk."""

        desk = self.get(desk_id)

        path: list[Desk] = []
        visited_ids: set[uuid.UUID] = set()

        current: Desk | None = desk

        while current is not None:
            if current.id in visited_ids:
                raise InvalidDeskError(
                    "The Desk hierarchy contains a cycle."
                )

            visited_ids.add(current.id)
            path.append(current)
            current = current.parent

        path.reverse()
        return path

    def descendants(
        self,
        desk_id: uuid.UUID,
        *,
        active_only: bool = False,
    ) -> list[Desk]:
        """Return every descendant beneath a Desk."""

        self.get(desk_id)

        descendants: list[Desk] = []
        pending_parent_ids: list[uuid.UUID] = [
            desk_id
        ]
        visited_ids: set[uuid.UUID] = {
            desk_id
        }

        while pending_parent_ids:
            parent_id = pending_parent_ids.pop(0)

            statement = (
                select(Desk)
                .where(
                    Desk.parent_id == parent_id
                )
                .order_by(
                    Desk.name,
                    Desk.code,
                )
            )

            children = list(
                self.session.scalars(
                    statement
                ).all()
            )

            for child in children:
                if child.id in visited_ids:
                    raise InvalidDeskError(
                        "The Desk hierarchy contains a cycle."
                    )

                visited_ids.add(child.id)

                if (
                    not active_only
                    or child.is_active
                ):
                    descendants.append(child)

                pending_parent_ids.append(
                    child.id
                )

        return descendants

    @staticmethod
    def _base_list_query() -> Select[tuple[Desk]]:
        return select(Desk).order_by(
            Desk.is_root.desc(),
            Desk.name,
            Desk.code,
        )