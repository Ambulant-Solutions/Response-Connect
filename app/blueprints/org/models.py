from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

class LocationUse(StrEnum):
    STAFF_BASE = "staff_base"
    VEHICLE_BASE = "vehicle_base"
    STOCK_STORAGE = "stock_storage"
    EQUIPMENT_STORAGE = "equipment_storage"
    MEDICATION_STORAGE = "medication_storage"
    CONTROLLED_DRUG_STORAGE = "controlled_drug_storage"
    DOCUMENT_STORAGE = "document_storage"


location_type_capabilities = Table(
    "location_type_capabilities",
    db.metadata,
    Column(
        "location_type_id",
        UUID(as_uuid=True),
        ForeignKey("location_types.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "capability_id",
        UUID(as_uuid=True),
        ForeignKey("location_capabilities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


location_capabilities = Table(
    "organisation_location_capabilities",
    db.metadata,
    Column(
        "location_id",
        UUID(as_uuid=True),
        ForeignKey("organisation_locations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "capability_id",
        UUID(as_uuid=True),
        ForeignKey("location_capabilities.id", ondelete="RESTRICT"),
        primary_key=True,
    ),
)


class LocationCapability(db.Model):
    """
    A fixed capability understood by application business logic.

    Administrators choose which capabilities apply to types and locations,
    but capability codes should not be freely renamed because other modules
    use these codes to validate assignments.
    """

    __tablename__ = "location_capabilities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    icon: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="tabler:map-pin",
        server_default="tabler:map-pin",
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    location_types: Mapped[list["LocationType"]] = relationship(
        secondary=location_type_capabilities,
        back_populates="allowed_capabilities",
    )

    locations: Mapped[list["OrganisationLocation"]] = relationship(
        secondary=location_capabilities,
        back_populates="capabilities",
    )


class LocationType(db.Model):
    """
    A configurable physical or organisational location classification.
    """

    __tablename__ = "location_types"

    __table_args__ = (
        UniqueConstraint(
            "code",
            name="uq_location_types_code",
        ),
        UniqueConstraint(
            "name",
            name="uq_location_types_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    code: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    icon: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        default="tabler:map-pin",
        server_default="tabler:map-pin",
    )

    is_physical: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    can_have_children: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    requires_address: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
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

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    allowed_capabilities: Mapped[list[LocationCapability]] = relationship(
        secondary=location_type_capabilities,
        back_populates="location_types",
        order_by="LocationCapability.sort_order",
    )

    locations: Mapped[list["OrganisationLocation"]] = relationship(
        back_populates="location_type",
    )

    @property
    def allowed_capability_codes(self) -> set[str]:
        return {
            capability.code
            for capability in self.allowed_capabilities
        }


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
        order_by=lambda: (
            OrganisationLocation.sort_order,
            OrganisationLocation.name,
        ),
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
    A node in the organisation's location hierarchy.

    The primary location is the single root node. Every other location must
    have a parent, allowing sites, departments, rooms, cupboards and storage
    areas to form one tree.
    """

    __tablename__ = "organisation_locations"

    __table_args__ = (
        Index(
            "uq_organisation_locations_single_primary",
            "organisation_id",
            unique=True,
            postgresql_where=text("is_primary IS TRUE"),
        ),
        UniqueConstraint(
            "organisation_id",
            "code",
            name="uq_organisation_locations_org_code",
        ),
        CheckConstraint(
            """
            (
                is_primary IS TRUE
                AND parent_id IS NULL
            )
            OR
            (
                is_primary IS FALSE
                AND parent_id IS NOT NULL
            )
            """,
            name="ck_organisation_locations_primary_root",
        ),
        CheckConstraint(
            "sort_order >= 0",
            name="ck_organisation_locations_sort_order",
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

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "organisation_locations.id",
            ondelete="RESTRICT",
        ),
        nullable=True,
        index=True,
    )

    location_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("location_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Child locations normally inherit their postal address from an ancestor.
    has_own_address: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    address_line_1: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address_line_2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    address_line_3: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    town_city: Mapped[str | None] = mapped_column(
        String(120),
        nullable=True,
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
        back_populates="locations",
    )

    location_type: Mapped[LocationType] = relationship(
        back_populates="locations",
    )

    parent: Mapped["OrganisationLocation | None"] = relationship(
        "OrganisationLocation",
        remote_side="OrganisationLocation.id",
        back_populates="children",
        foreign_keys=[parent_id],
    )

    children: Mapped[list["OrganisationLocation"]] = relationship(
        "OrganisationLocation",
        back_populates="parent",
        foreign_keys=[parent_id],
        passive_deletes=True,
        order_by=lambda: (
            OrganisationLocation.sort_order,
            OrganisationLocation.name,
        ),
    )

    capabilities: Mapped[list[LocationCapability]] = relationship(
        secondary=location_capabilities,
        back_populates="locations",
        order_by="LocationCapability.sort_order",
    )

    @property
    def capability_codes(self) -> set[str]:
        return {
            capability.code
            for capability in self.capabilities
            if capability.is_active
        }

    def permits(self, capability: str | LocationUse) -> bool:
        code = (
            capability.value
            if isinstance(capability, LocationUse)
            else capability
        )

        return self.is_active and code in self.capability_codes

    @property
    def effective_address_location(
        self,
    ) -> "OrganisationLocation | None":
        current: OrganisationLocation | None = self
        visited: set[uuid.UUID] = set()

        while current is not None:
            if current.id in visited:
                return None

            visited.add(current.id)

            if current.has_own_address and current.address_line_1:
                return current

            current = current.parent

        return None

    @property
    def formatted_address(self) -> str | None:
        source = self.effective_address_location

        if source is None:
            return None

        parts = [
            source.address_line_1,
            source.address_line_2,
            source.address_line_3,
            source.town_city,
            source.county_region,
            source.postcode,
        ]

        return ", ".join(part for part in parts if part)

    @property
    def path(self) -> str:
        parts: list[str] = []
        current: OrganisationLocation | None = self
        visited: set[uuid.UUID] = set()

        while current is not None:
            if current.id in visited:
                parts.append("[invalid hierarchy]")
                break

            visited.add(current.id)
            parts.append(current.name)
            current = current.parent

        return " / ".join(reversed(parts))

    def __repr__(self) -> str:
        return f"<OrganisationLocation {self.path!r}>"
   