from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Organisation(db.Model):
    """
    The organisation that owns and operates this Response Connect installation.

    A normal installation will have one organisation marked as primary. The
    structure still allows additional related legal entities to be added later.
    """

    __tablename__ = "organisations"

    __table_args__ = (
        Index(
            "uq_organisations_single_primary",
            "is_primary",
            unique=True,
            postgresql_where=text("is_primary IS TRUE"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Organisation identity
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    legal_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    service_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Generic regulator/provider reference, for example a CQC provider ID.
    provider_reference: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
        unique=True,
    )

    company_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
    )

    charity_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
    )

    vat_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        unique=True,
    )

    # Primary contact information
    general_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    general_phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    website_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # General operating area, rather than a postal address.
    region: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    # Installation-wide regional settings
    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="GB",
        server_default="GB",
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        default="Europe/London",
        server_default="Europe/London",
    )

    locale: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="en-GB",
        server_default="en-GB",
    )

    is_primary: Mapped[bool] = mapped_column(
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

    locations: Mapped[list["OrganisationLocation"]] = relationship(
        "OrganisationLocation",
        back_populates="organisation",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="OrganisationLocation.name",
    )

    @property
    def initials(self) -> str:
        words = [
            word
            for word in self.name.replace("&", " ").split()
            if word.lower() not in {"and", "the", "of"}
        ]

        if not words:
            return "RC"

        if len(words) == 1:
            return words[0][:2].upper()

        return "".join(word[0].upper() for word in words[:3])

    @property
    def primary_location_record(self) -> "OrganisationLocation | None":
        return next(
            (
                location
                for location in self.locations
                if location.is_primary and location.is_active
            ),
            None,
        )

    @property
    def primary_location(self) -> str | None:
        location = self.primary_location_record
        return location.name if location else None

    def __repr__(self) -> str:
        return f"<Organisation {self.name!r}>"


class OrganisationLocation(db.Model):
    """
    A physical organisation location.

    Examples include a registered office, headquarters, ambulance station,
    operational base, warehouse or training centre.
    """

    __tablename__ = "organisation_locations"

    __table_args__ = (
        Index(
            "uq_organisation_locations_primary_type",
            "organisation_id",
            "location_type",
            unique=True,
            postgresql_where=text("is_primary IS TRUE"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Examples: registered_office, head_office, operational_base,
    # ambulance_station, warehouse, training_centre, other.
    location_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="operational_base",
        server_default="operational_base",
    )

    address_line_1: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    address_line_2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address_line_3: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    town_city: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    county_region: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
    )

    postcode: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    country_code: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
        default="GB",
        server_default="GB",
    )

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    is_primary: Mapped[bool] = mapped_column(
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

    organisation: Mapped[Organisation] = relationship(
        "Organisation",
        back_populates="locations",
    )

    @property
    def formatted_address(self) -> str:
        parts = [
            self.address_line_1,
            self.address_line_2,
            self.address_line_3,
            self.town_city,
            self.county_region,
            self.postcode,
        ]

        return ", ".join(part for part in parts if part)

    def __repr__(self) -> str:
        return f"<OrganisationLocation {self.name!r}>"