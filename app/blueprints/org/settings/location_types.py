from __future__ import annotations

import re
import uuid

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    url_for,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.blueprints.auth import permission_required
from app.blueprints.org.models import (
    LocationCapability,
    LocationType,
    OrganisationLocation,
)
from app.blueprints.org.settings import settings_bp
from app.blueprints.org.settings.forms import (
    LocationTypeActionForm,
    LocationTypeForm,
)
from app.blueprints.org.settings.location_defaults import (
    ensure_default_location_catalogue,
)
from app.extensions import db


LOCATION_TYPE_CODE_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)


def normalise_code(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()
    return value or None


def load_capabilities() -> list[LocationCapability]:
    statement = select(LocationCapability).order_by(
        LocationCapability.sort_order,
        LocationCapability.name,
    )

    return list(db.session.scalars(statement).all())


def load_location_types() -> list[LocationType]:
    statement = (
        select(LocationType)
        .options(
            selectinload(
                LocationType.allowed_capabilities
            ),
            selectinload(
                LocationType.locations
            ).selectinload(
                OrganisationLocation.capabilities
            ),
            selectinload(
                LocationType.locations
            ).selectinload(
                OrganisationLocation.children
            ),
        )
        .order_by(
            LocationType.sort_order,
            LocationType.name,
        )
    )

    return list(
        db.session.scalars(statement).unique().all()
    )


def get_location_type_or_404(
    location_type_id: uuid.UUID,
) -> LocationType:
    statement = (
        select(LocationType)
        .where(LocationType.id == location_type_id)
        .options(
            selectinload(
                LocationType.allowed_capabilities
            ),
            selectinload(
                LocationType.locations
            ).selectinload(
                OrganisationLocation.capabilities
            ),
            selectinload(
                LocationType.locations
            ).selectinload(
                OrganisationLocation.children
            ),
        )
    )

    location_type = db.session.scalar(statement)

    if location_type is None:
        abort(404)

    return location_type


def configure_location_type_form(
    form: LocationTypeForm,
    capabilities: list[LocationCapability],
    current_type: LocationType | None = None,
) -> None:
    selected_ids = {
        capability.id
        for capability in (
            current_type.allowed_capabilities
            if current_type is not None
            else []
        )
    }

    form.capability_ids.choices = [
        (
            str(capability.id),
            capability.name,
        )
        for capability in capabilities
        if capability.is_active
        or capability.id in selected_ids
    ]


def validate_location_type_form(
    form: LocationTypeForm,
    *,
    capabilities: list[LocationCapability],
    current_type: LocationType | None,
) -> tuple[bool, list[LocationCapability]]:
    valid = True

    code = normalise_code(form.code.data)

    if not LOCATION_TYPE_CODE_PATTERN.fullmatch(code):
        form.code.errors.append(
            "Use lowercase letters, numbers and underscores only. "
            "The code must begin with a letter."
        )
        valid = False

    code_statement = select(LocationType.id).where(
        func.lower(LocationType.code) == code.lower()
    )

    name_statement = select(LocationType.id).where(
        func.lower(LocationType.name)
        == form.name.data.strip().lower()
    )

    if current_type is not None:
        code_statement = code_statement.where(
            LocationType.id != current_type.id
        )

        name_statement = name_statement.where(
            LocationType.id != current_type.id
        )

    if db.session.scalar(code_statement) is not None:
        form.code.errors.append(
            "This location-type code is already in use."
        )
        valid = False

    if db.session.scalar(name_statement) is not None:
        form.name.errors.append(
            "This location-type name is already in use."
        )
        valid = False

    capability_by_id = {
        str(capability.id): capability
        for capability in capabilities
    }

    selected_capabilities: list[
        LocationCapability
    ] = []

    for capability_id in form.capability_ids.data or []:
        capability = capability_by_id.get(capability_id)

        if capability is None:
            form.capability_ids.errors.append(
                "One or more selected capabilities are invalid."
            )
            valid = False
            continue

        selected_capabilities.append(capability)

    if current_type is not None:
        code_locked = (
            current_type.is_system
            or bool(current_type.locations)
        )

        if code_locked and code != current_type.code:
            form.code.errors.append(
                "The code cannot be changed because this is a "
                "system type or it is already in use."
            )
            valid = False

        if (
            current_type.can_have_children
            and not form.can_have_children.data
            and any(
                location.children
                for location in current_type.locations
            )
        ):
            form.can_have_children.errors.append(
                "This option cannot be removed while locations of "
                "this type contain child locations."
            )
            valid = False

        current_capability_ids = {
            capability.id
            for capability in current_type.allowed_capabilities
        }

        selected_capability_ids = {
            capability.id
            for capability in selected_capabilities
        }

        removed_capability_ids = (
            current_capability_ids
            - selected_capability_ids
        )

        capabilities_in_use = {
            capability.id
            for location in current_type.locations
            for capability in location.capabilities
        }

        if removed_capability_ids & capabilities_in_use:
            form.capability_ids.errors.append(
                "A capability cannot be removed while a location "
                "of this type is using it."
            )
            valid = False

        if (
            form.requires_address.data
            and not current_type.requires_address
        ):
            locations_without_addresses = [
                location
                for location in current_type.locations
                if not (
                    location.has_own_address
                    and location.address_line_1
                    and location.town_city
                )
            ]

            if locations_without_addresses:
                form.requires_address.errors.append(
                    "This type cannot require an address until all "
                    "existing locations of this type have their own "
                    "complete address."
                )
                valid = False

    return valid, selected_capabilities


def apply_location_type_form(
    location_type: LocationType,
    *,
    form: LocationTypeForm,
    capabilities: list[LocationCapability],
) -> None:
    location_type.code = normalise_code(
        form.code.data
    )
    location_type.name = form.name.data.strip()
    location_type.description = optional_text(
        form.description.data
    )
    location_type.icon = (
        form.icon.data.strip()
        or "tabler:map-pin"
    )
    location_type.is_physical = (
        form.is_physical.data
    )
    location_type.can_have_children = (
        form.can_have_children.data
    )
    location_type.requires_address = (
        form.requires_address.data
    )
    location_type.sort_order = form.sort_order.data
    location_type.allowed_capabilities = capabilities


@settings_bp.get("/location-types")
@permission_required("org:manage")
def location_type_index():
    ensure_default_location_catalogue()

    location_types = load_location_types()

    return render_template(
        "org/settings/location_types/index.html",
        location_types=location_types,
        action_form=LocationTypeActionForm(),
        active_org_section="settings",
    )


@settings_bp.route(
    "/location-types/new",
    methods=["GET", "POST"],
)
@permission_required("org:manage")
def location_type_create():
    ensure_default_location_catalogue()

    capabilities = load_capabilities()
    form = LocationTypeForm()

    configure_location_type_form(
        form,
        capabilities,
    )

    base_valid = form.validate_on_submit()
    references_valid = False
    selected_capabilities = []

    if form.is_submitted():
        (
            references_valid,
            selected_capabilities,
        ) = validate_location_type_form(
            form,
            capabilities=capabilities,
            current_type=None,
        )

    if base_valid and references_valid:
        location_type = LocationType(
            is_system=False,
            is_active=True,
        )

        apply_location_type_form(
            location_type,
            form=form,
            capabilities=selected_capabilities,
        )

        db.session.add(location_type)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The location type could not be created. "
                "Check that its name and code are unique.",
                "danger",
            )
        else:
            flash(
                "Location type created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "org.settings.location_type_index"
                )
            )

    return render_template(
        "org/settings/location_types/form.html",
        form=form,
        location_type=None,
        code_locked=False,
        active_org_section="settings",
    )


@settings_bp.route(
    "/location-types/<uuid:location_type_id>/edit",
    methods=["GET", "POST"],
)
@permission_required("org:manage")
def location_type_edit(
    location_type_id: uuid.UUID,
):
    ensure_default_location_catalogue()

    location_type = get_location_type_or_404(
        location_type_id
    )
    capabilities = load_capabilities()
    form = LocationTypeForm()

    configure_location_type_form(
        form,
        capabilities,
        current_type=location_type,
    )

    if not form.is_submitted():
        form.code.data = location_type.code
        form.name.data = location_type.name
        form.description.data = (
            location_type.description
        )
        form.icon.data = location_type.icon
        form.is_physical.data = (
            location_type.is_physical
        )
        form.can_have_children.data = (
            location_type.can_have_children
        )
        form.requires_address.data = (
            location_type.requires_address
        )
        form.capability_ids.data = [
            str(capability.id)
            for capability
            in location_type.allowed_capabilities
        ]
        form.sort_order.data = (
            location_type.sort_order
        )

    base_valid = form.validate_on_submit()
    references_valid = False
    selected_capabilities = []

    if form.is_submitted():
        (
            references_valid,
            selected_capabilities,
        ) = validate_location_type_form(
            form,
            capabilities=capabilities,
            current_type=location_type,
        )

    if base_valid and references_valid:
        apply_location_type_form(
            location_type,
            form=form,
            capabilities=selected_capabilities,
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The location type could not be saved. "
                "Check that its name and code are unique.",
                "danger",
            )
        else:
            flash(
                "Location type updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "org.settings.location_type_index"
                )
            )

    return render_template(
        "org/settings/location_types/form.html",
        form=form,
        location_type=location_type,
        code_locked=(
            location_type.is_system
            or bool(location_type.locations)
        ),
        active_org_section="settings",
    )


@settings_bp.post(
    "/location-types/<uuid:location_type_id>/deactivate"
)
@permission_required("org:manage")
def location_type_deactivate(
    location_type_id: uuid.UUID,
):
    form = LocationTypeActionForm()

    if not form.validate_on_submit():
        abort(400)

    location_type = get_location_type_or_404(
        location_type_id
    )

    active_location_count = db.session.scalar(
        select(func.count())
        .select_from(OrganisationLocation)
        .where(
            OrganisationLocation.location_type_id
            == location_type.id,
            OrganisationLocation.is_active.is_(True),
        )
    ) or 0

    if active_location_count:
        flash(
            "This type cannot be deactivated while active "
            "locations use it.",
            "danger",
        )
    else:
        location_type.is_active = False
        db.session.commit()

        flash(
            "Location type deactivated.",
            "success",
        )

    return redirect(
        url_for("org.settings.location_type_index")
    )


@settings_bp.post(
    "/location-types/<uuid:location_type_id>/activate"
)
@permission_required("org:manage")
def location_type_activate(
    location_type_id: uuid.UUID,
):
    form = LocationTypeActionForm()

    if not form.validate_on_submit():
        abort(400)

    location_type = get_location_type_or_404(
        location_type_id
    )
    location_type.is_active = True
    db.session.commit()

    flash(
        "Location type activated.",
        "success",
    )

    return redirect(
        url_for("org.settings.location_type_index")
    )