from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.catalogues.constants import (
    DEFAULT_CATALOGUE_COLOUR,
    DEFAULT_CATALOGUE_ICON,
    DEFAULT_CATALOGUE_SORT_ORDER,
    MAX_CATALOGUE_CODE_LENGTH,
    MAX_CATALOGUE_COLOUR_LENGTH,
    MAX_CATALOGUE_DESCRIPTION_LENGTH,
    MAX_CATALOGUE_ICON_LENGTH,
    MAX_CATALOGUE_NAME_LENGTH,
)


class CatalogueMixin:
    """
    Shared fields and simple display helpers for concrete catalogue models.

    This mixin does not create a table of its own.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[str] = mapped_column(
        String(MAX_CATALOGUE_CODE_LENGTH),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(MAX_CATALOGUE_NAME_LENGTH),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(MAX_CATALOGUE_DESCRIPTION_LENGTH),
        nullable=True,
    )

    icon: Mapped[str] = mapped_column(
        String(MAX_CATALOGUE_ICON_LENGTH),
        nullable=False,
        default=DEFAULT_CATALOGUE_ICON,
        server_default=DEFAULT_CATALOGUE_ICON,
    )

    colour: Mapped[str] = mapped_column(
        String(MAX_CATALOGUE_COLOUR_LENGTH),
        nullable=False,
        default=DEFAULT_CATALOGUE_COLOUR,
        server_default=DEFAULT_CATALOGUE_COLOUR,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=DEFAULT_CATALOGUE_SORT_ORDER,
        server_default=str(DEFAULT_CATALOGUE_SORT_ORDER),
    )

    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    @property
    def display_name(self) -> str:
        return self.name

    @property
    def is_custom(self) -> bool:
        return not self.is_system