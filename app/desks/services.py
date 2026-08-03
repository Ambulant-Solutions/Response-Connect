"""Desk lifecycle and hierarchy services."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import (
    IntegrityError,
    SQLAlchemyError,
)
from sqlalchemy.orm import Session

from app.desks.commands import (
    CreateDeskCommand,
    MoveDeskCommand,
    UpdateDeskCommand,
)
from app.desks.exceptions import (
    DeskConflictError,
    DeskHierarchyError,
    DeskNotFoundError,
    DeskPersistenceError,
    InvalidDeskError,
)
from app.desks.models import Desk
from app.desks.validators import (
    validate_desk_code,
    validate_desk_description,
    validate_desk_name,
)


class DeskService:
    """Create and update Desks.

    Public mutation methods own their database transaction unless
    explicitly documented otherwise.
    """

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def bootstrap_root(
        self,
        *,
        code: str,
        name: str,
        description: str | None = None,
    ) -> Desk:
        """Return the existing root Desk or create it.

        This operation is idempotent. If a root Desk already exists, its
        current values are preserved rather than overwritten.
        """

        existing_root = self.session.scalar(
            select(Desk).where(
                Desk.is_root.is_(True)
            )
        )

        if existing_root is not None:
            return existing_root

        validated_code = validate_desk_code(code)
        validated_name = validate_desk_name(name)
        validated_description = (
            validate_desk_description(description)
        )

        self._ensure_code_available(
            validated_code
        )

        root = Desk(
            code=validated_code,
            name=validated_name,
            description=validated_description,
            parent_id=None,
            is_root=True,
            is_active=True,
        )

        self.session.add(root)

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()

            # Another process may have created the root between our
            # initial lookup and commit. Return that root where possible,
            # preserving idempotent bootstrap behaviour.
            existing_root = self.session.scalar(
                select(Desk).where(
                    Desk.is_root.is_(True)
                )
            )

            if existing_root is not None:
                return existing_root

            raise DeskConflictError(
                "The root Desk could not be created "
                "because it conflicts with existing "
                "Desk data."
            ) from exc
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise DeskPersistenceError(
                "The root Desk could not be saved."
            ) from exc

        return root

    def create(
        self,
        command: CreateDeskCommand,
    ) -> Desk:
        """Create and return a Desk."""

        code = validate_desk_code(
            command.code
        )
        name = validate_desk_name(
            command.name
        )
        description = validate_desk_description(
            command.description
        )

        self._ensure_code_available(code)

        if command.is_root:
            self._validate_new_root(
                parent_id=command.parent_id,
            )
            parent = None
        else:
            if command.parent_id is None:
                raise InvalidDeskError(
                    "A parent Desk is required for "
                    "a non-root Desk."
                )

            parent = self._get_desk(
                command.parent_id,
                description="parent Desk",
            )

        desk = Desk(
            code=code,
            name=name,
            description=description,
            parent=parent,
            is_root=command.is_root,
            is_active=True,
        )

        self.session.add(desk)

        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            self._raise_create_conflict(
                code=code,
                is_root=command.is_root,
                cause=exc,
            )
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise DeskPersistenceError(
                "The Desk could not be created."
            ) from exc

        return desk

    def update(
        self,
        desk_id: uuid.UUID,
        command: UpdateDeskCommand,
    ) -> Desk:
        """Update editable Desk fields and return the Desk."""

        desk = self._get_desk(desk_id)

        name = validate_desk_name(
            command.name
        )
        description = validate_desk_description(
            command.description
        )

        desk.name = name
        desk.description = description

        try:
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise DeskPersistenceError(
                "The Desk could not be updated."
            ) from exc

        return desk

    def move(
        self,
        desk_id: uuid.UUID,
        command: MoveDeskCommand,
    ) -> Desk:
        """Move a Desk beneath a new parent."""

        desk = self._get_desk(desk_id)
        new_parent = self._get_desk(
            command.parent_id,
            description="parent Desk",
        )

        if desk.is_root:
            raise DeskHierarchyError(
                "The root Desk cannot be moved."
            )

        if desk.id == new_parent.id:
            raise DeskHierarchyError(
                "A Desk cannot be moved beneath itself."
            )

        if desk.parent_id == new_parent.id:
            return desk

        if self._is_descendant(
            possible_descendant_id=new_parent.id,
            ancestor_id=desk.id,
        ):
            raise DeskHierarchyError(
                "A Desk cannot be moved beneath one "
                "of its descendants."
            )

        desk.parent = new_parent

        try:
            self.session.commit()
        except SQLAlchemyError as exc:
            self.session.rollback()
            raise DeskPersistenceError(
                "The Desk could not be moved."
            ) from exc

        return desk

    def _get_desk(
        self,
        desk_id: uuid.UUID,
        *,
        description: str = "Desk",
    ) -> Desk:
        desk = self.session.get(
            Desk,
            desk_id,
        )

        if desk is None:
            raise DeskNotFoundError(
                f"The {description} could not be found."
            )

        return desk

    def _ensure_code_available(
        self,
        code: str,
    ) -> None:
        existing_id = self.session.scalar(
            select(Desk.id).where(
                Desk.code == code
            )
        )

        if existing_id is not None:
            raise DeskConflictError(
                "A Desk already uses code "
                f"{code!r}."
            )

    def _validate_new_root(
        self,
        *,
        parent_id: uuid.UUID | None,
    ) -> None:
        if parent_id is not None:
            raise InvalidDeskError(
                "The root Desk cannot have a parent."
            )

        existing_root_id = self.session.scalar(
            select(Desk.id).where(
                Desk.is_root.is_(True)
            )
        )

        if existing_root_id is not None:
            raise DeskConflictError(
                "A root Desk already exists."
            )

    def _raise_create_conflict(
        self,
        *,
        code: str,
        is_root: bool,
        cause: IntegrityError,
    ) -> None:
        """Translate a creation integrity failure."""

        existing_code = self.session.scalar(
            select(Desk.id).where(
                Desk.code == code
            )
        )

        if existing_code is not None:
            raise DeskConflictError(
                "A Desk already uses code "
                f"{code!r}."
            ) from cause

        if is_root:
            existing_root = self.session.scalar(
                select(Desk.id).where(
                    Desk.is_root.is_(True)
                )
            )

            if existing_root is not None:
                raise DeskConflictError(
                    "A root Desk already exists."
                ) from cause

        raise DeskConflictError(
            "The Desk could not be created because "
            "it conflicts with existing Desk data."
        ) from cause

    def _is_descendant(
        self,
        *,
        possible_descendant_id: uuid.UUID,
        ancestor_id: uuid.UUID,
    ) -> bool:
        """Return whether one Desk is beneath another."""

        current_id: uuid.UUID | None = (
            possible_descendant_id
        )
        visited_ids: set[uuid.UUID] = set()

        while current_id is not None:
            if current_id in visited_ids:
                raise DeskHierarchyError(
                    "The Desk hierarchy contains a cycle."
                )

            visited_ids.add(current_id)

            if current_id == ancestor_id:
                return True

            current_id = self.session.scalar(
                select(Desk.parent_id).where(
                    Desk.id == current_id
                )
            )

        return False