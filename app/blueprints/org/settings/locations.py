from __future__ import annotations

import uuid
from typing import Any

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    current_app
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.blueprints.auth import permission_required
from app.blueprints.org.models import (
    LocationCapability,
    LocationType,
    LocationUse,
    OrganisationLocation,
)
from app.blueprints.org.services import (
    clear_current_organisation,
    require_current_organisation,
)
from app.blueprints.org.settings import settings_bp
from app.blueprints.org.settings.forms import (
    LocationActionForm,
    LocationForm,
)

from app.blueprints.org.settings.location_defaults import (
    ensure_default_location_catalogue,
)

from app.extensions import db


def optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()
    return value or None


def load_locations(
    organisation_id: uuid.UUID,
) -> list[OrganisationLocation]:
    statement = (
        select(OrganisationLocation)
        .where(
            OrganisationLocation.organisation_id
            == organisation_id
        )
        .options(
            selectinload(
                OrganisationLocation.location_type
            ),
            selectinload(
                OrganisationLocation.capabilities
            ),
            selectinload(
                OrganisationLocation.parent
            ),
        )
        .order_by(
            OrganisationLocation.sort_order,
            OrganisationLocation.name,
        )
    )

    return list(
        db.session.scalars(statement).unique().all()
    )


def load_location_types() -> list[LocationType]:
    statement = (
        select(LocationType)
        .options(
            selectinload(
                LocationType.allowed_capabilities
            )
        )
        .order_by(
            LocationType.sort_order,
            LocationType.name,
        )
    )

    return list(
        db.session.scalars(statement).unique().all()
    )


def load_capabilities() -> list[LocationCapability]:
    statement = select(LocationCapability).order_by(
        LocationCapability.sort_order,
        LocationCapability.name,
    )

    return list(db.session.scalars(statement).all())


def get_location_or_404(
    organisation_id: uuid.UUID,
    location_id: uuid.UUID,
) -> OrganisationLocation:
    statement = (
        select(OrganisationLocation)
        .where(
            OrganisationLocation.id == location_id,
            OrganisationLocation.organisation_id
            == organisation_id,
        )
        .options(
            selectinload(
                OrganisationLocation.location_type
            ),
            selectinload(
                OrganisationLocation.capabilities
            ),
            selectinload(
                OrganisationLocation.children
            ),
            selectinload(
                OrganisationLocation.parent
            ),
        )
    )

    location = db.session.scalar(statement)

    if location is None:
        abort(404)

    return location


def build_location_tree(
    locations: list[OrganisationLocation],
) -> list[dict[str, Any]]:
    nodes = {
        location.id: {
            "location": location,
            "children": [],
        }
        for location in locations
    }

    roots: list[dict[str, Any]] = []

    for location in locations:
        node = nodes[location.id]

        if (
            location.parent_id is not None
            and location.parent_id in nodes
        ):
            nodes[location.parent_id]["children"].append(
                node
            )
        else:
            roots.append(node)

    def sort_nodes(items: list[dict[str, Any]]) -> None:
        items.sort(
            key=lambda item: (
                item["location"].sort_order,
                item["location"].name.casefold(),
            )
        )

        for item in items:
            sort_nodes(item["children"])

    sort_nodes(roots)
    return roots


def get_descendant_ids(
    location_id: uuid.UUID,
    locations: list[OrganisationLocation],
) -> set[uuid.UUID]:
    children_by_parent: dict[
        uuid.UUID,
        list[uuid.UUID],
    ] = {}

    for location in locations:
        if location.parent_id is None:
            continue

        children_by_parent.setdefault(
            location.parent_id,
            [],
        ).append(location.id)

    descendants: set[uuid.UUID] = set()
    pending = list(
        children_by_parent.get(location_id, [])
    )

    while pending:
        child_id = pending.pop()

        if child_id in descendants:
            continue

        descendants.add(child_id)
        pending.extend(
            children_by_parent.get(child_id, [])
        )

    return descendants


def configure_location_form(
    form: LocationForm,
    *,
    locations: list[OrganisationLocation],
    location_types: list[LocationType],
    capabilities: list[LocationCapability],
    current_location: OrganisationLocation | None,
) -> None:
    form.location_type_id.choices = [
        (
            str(location_type.id),
            (
                location_type.name
                if location_type.is_active
                else f"{location_type.name} (inactive)"
            ),
        )
        for location_type in location_types
        if (
            location_type.is_active
            or (
                current_location is not None
                and current_location.location_type_id
                == location_type.id
            )
        )
    ]

    excluded_ids: set[uuid.UUID] = set()

    if current_location is not None:
        excluded_ids.add(current_location.id)
        excluded_ids.update(
            get_descendant_ids(
                current_location.id,
                locations,
            )
        )

    parent_choices = [
        ("", "Select a parent location")
    ]

    for location in locations:
        if location.id in excluded_ids:
            continue

        if not location.is_active:
            continue

        if not location.location_type.can_have_children:
            continue

        parent_choices.append(
            (
                str(location.id),
                location.path,
            )
        )

    form.parent_id.choices = parent_choices

    form.capability_ids.choices = [
        (
            str(capability.id),
            capability.name,
        )
        for capability in capabilities
        if capability.is_active
    ]


def resolve_location_form(
    form: LocationForm,
    *,
    organisation_id: uuid.UUID,
    locations: list[OrganisationLocation],
    location_types: list[LocationType],
    capabilities: list[LocationCapability],
    current_location: OrganisationLocation | None,
    is_primary: bool,
) -> tuple[
    bool,
    LocationType | None,
    OrganisationLocation | None,
    list[LocationCapability],
]:
    valid = True

    location_types_by_id = {
        str(location_type.id): location_type
        for location_type in location_types
    }

    capabilities_by_id = {
        str(capability.id): capability
        for capability in capabilities
    }

    locations_by_id = {
        str(location.id): location
        for location in locations
    }

    location_type = location_types_by_id.get(
        form.location_type_id.data
    )

    if location_type is None:
        form.location_type_id.errors.append(
            "Select a valid location type."
        )
        valid = False

    parent: OrganisationLocation | None = None

    if is_primary:
        if form.parent_id.data:
            form.parent_id.errors.append(
                "The primary location cannot have a parent."
            )
            valid = False

        if (
            location_type is not None
            and not location_type.can_have_children
        ):
            form.location_type_id.errors.append(
                "The primary location must use a type "
                "that can contain child locations."
            )
            valid = False
    else:
        parent = locations_by_id.get(
            form.parent_id.data
        )

        if parent is None:
            form.parent_id.errors.append(
                "Select a parent location."
            )
            valid = False
        else:
            if parent.organisation_id != organisation_id:
                form.parent_id.errors.append(
                    "The parent belongs to another organisation."
                )
                valid = False

            if not parent.is_active:
                form.parent_id.errors.append(
                    "The parent location is inactive."
                )
                valid = False

            if not parent.location_type.can_have_children:
                form.parent_id.errors.append(
                    "The selected parent cannot contain "
                    "child locations."
                )
                valid = False

            if current_location is not None:
                invalid_parent_ids = get_descendant_ids(
                    current_location.id,
                    locations,
                )
                invalid_parent_ids.add(
                    current_location.id
                )

                if parent.id in invalid_parent_ids:
                    form.parent_id.errors.append(
                        "A location cannot be moved beneath "
                        "itself or one of its descendants."
                    )
                    valid = False

    selected_capabilities: list[
        LocationCapability
    ] = []

    unknown_capability = False

    for capability_id in form.capability_ids.data:
        capability = capabilities_by_id.get(
            capability_id
        )

        if capability is None:
            unknown_capability = True
            continue

        selected_capabilities.append(capability)

    if unknown_capability:
        form.capability_ids.errors.append(
            "One or more selected uses are invalid."
        )
        valid = False

    if location_type is not None:
        allowed_ids = {
            str(capability.id)
            for capability
            in location_type.allowed_capabilities
        }

        invalid_capabilities = [
            capability
            for capability in selected_capabilities
            if str(capability.id) not in allowed_ids
        ]

        if invalid_capabilities:
            form.capability_ids.errors.append(
                "One or more selected uses are not "
                "permitted for this location type."
            )
            valid = False

    selected_codes = {
        capability.code
        for capability in selected_capabilities
    }

    if (
        LocationUse.CONTROLLED_DRUG_STORAGE.value
        in selected_codes
        and LocationUse.MEDICATION_STORAGE.value
        not in selected_codes
    ):
        form.capability_ids.errors.append(
            "Controlled-drug storage also requires "
            "medication storage."
        )
        valid = False

    if (
        current_location is not None
        and current_location.children
        and location_type is not None
        and not location_type.can_have_children
    ):
        form.location_type_id.errors.append(
            "This location already has child locations, "
            "so its type must allow children."
        )
        valid = False

    requires_address = (
        location_type is not None
        and location_type.requires_address
    )

    has_address = (
        requires_address
        or form.has_own_address.data
    )

    if has_address:
        if not optional_text(
            form.address_line_1.data
        ):
            form.address_line_1.errors.append(
                "Address line 1 is required."
            )
            valid = False

        if not optional_text(form.town_city.data):
            form.town_city.errors.append(
                "Town or city is required."
            )
            valid = False

    code = optional_text(form.code.data)

    if code is not None:
        statement = select(
            OrganisationLocation.id
        ).where(
            OrganisationLocation.organisation_id
            == organisation_id,
            func.lower(OrganisationLocation.code)
            == code.lower(),
        )

        if current_location is not None:
            statement = statement.where(
                OrganisationLocation.id
                != current_location.id
            )

        if db.session.scalar(statement) is not None:
            form.code.errors.append(
                "This location code is already in use."
            )
            valid = False

    return (
        valid,
        location_type,
        parent,
        selected_capabilities,
    )


def apply_location_form(
    location: OrganisationLocation,
    *,
    form: LocationForm,
    location_type: LocationType,
    parent: OrganisationLocation | None,
    capabilities: list[LocationCapability],
    is_primary: bool,
) -> None:
    location.name = form.name.data.strip()
    location.code = optional_text(form.code.data)

    if location.code:
        location.code = location.code.upper()

    location.description = optional_text(
        form.description.data
    )
    location.location_type = location_type
    location.parent = None if is_primary else parent
    location.is_primary = is_primary
    location.sort_order = form.sort_order.data
    location.capabilities = capabilities

    location.has_own_address = (
        location_type.requires_address
        or form.has_own_address.data
    )

    location.country_code = (
        form.country_code.data.strip().upper()
    )

    location.phone = optional_text(form.phone.data)
    location.email = optional_text(form.email.data)

    if location.email:
        location.email = location.email.lower()

    if location.has_own_address:
        location.address_line_1 = optional_text(
            form.address_line_1.data
        )
        location.address_line_2 = optional_text(
            form.address_line_2.data
        )
        location.address_line_3 = optional_text(
            form.address_line_3.data
        )
        location.town_city = optional_text(
            form.town_city.data
        )
        location.county_region = optional_text(
            form.county_region.data
        )
        location.postcode = optional_text(
            form.postcode.data
        )

        if location.postcode:
            location.postcode = (
                location.postcode.upper()
            )
    else:
        location.address_line_1 = None
        location.address_line_2 = None
        location.address_line_3 = None
        location.town_city = None
        location.county_region = None
        location.postcode = None

def build_location_type_data(
    location_types: list[LocationType],
) -> dict[str, dict]:
    return {
        str(location_type.id): {
            "allowed": [
                str(capability.id)
                for capability
                in location_type.allowed_capabilities
            ],
            "requires_address": (
                location_type.requires_address
            ),
        }
        for location_type in location_types
    }


@settings_bp.get("/locations")
@permission_required("org:manage")
def location_index():
    seed_result = ensure_default_location_catalogue()

    if seed_result.changed:
        current_app.logger.info(
            "Created %s location capabilities and %s location types.",
            seed_result.capabilities_created,
            seed_result.location_types_created,
        )
    
    organisation = require_current_organisation()
    locations = load_locations(organisation.id)

    location_by_id = {
        str(location.id): location
        for location in locations
    }

    selected = location_by_id.get(
        request.args.get("selected", "")
    )

    if selected is None:
        selected = next(
            (
                location
                for location in locations
                if location.is_primary
            ),
            locations[0] if locations else None,
        )

    return render_template(
        "org/settings/locations/index.html",
        organisation=organisation,
        location_tree=build_location_tree(locations),
        locations=locations,
        selected_location=selected,
        active_location_count=sum(
            1
            for location in locations
            if location.is_active
        ),
        action_form=LocationActionForm(),
        active_org_section="settings",
    )


@settings_bp.route(
    "/locations/new",
    methods=["GET", "POST"],
)
@permission_required("org:manage")
def location_create():
    seed_result = ensure_default_location_catalogue()

    if seed_result.changed:
        current_app.logger.info(
            "Created %s location capabilities and %s location types.",
            seed_result.capabilities_created,
            seed_result.location_types_created,
        )
    
    organisation = require_current_organisation()
    locations = load_locations(organisation.id)
    location_types = load_location_types()
    capabilities = load_capabilities()

    primary_location = next(
        (
            location
            for location in locations
            if location.is_primary
        ),
        None,
    )

    is_primary = primary_location is None

    form = LocationForm()

    configure_location_form(
        form,
        locations=locations,
        location_types=location_types,
        capabilities=capabilities,
        current_location=None,
    )

    if not form.is_submitted():
        parent_id = request.args.get("parent")

        if (
            not is_primary
            and parent_id
            and any(
                str(location.id) == parent_id
                for location in locations
            )
        ):
            form.parent_id.data = parent_id
        elif not is_primary and primary_location:
            form.parent_id.data = str(
                primary_location.id
            )

        default_type = next(
            (
                location_type
                for location_type in location_types
                if (
                    location_type.is_active
                    and (
                        not is_primary
                        or location_type.can_have_children
                    )
                )
            ),
            None,
        )

        if default_type:
            form.location_type_id.data = str(
                default_type.id
            )

        form.country_code.data = (
            organisation.country_code
        )
        form.has_own_address.data = is_primary

    base_valid = form.validate_on_submit()

    references_valid = False
    location_type = None
    parent = None
    selected_capabilities = []

    if form.is_submitted():
        (
            references_valid,
            location_type,
            parent,
            selected_capabilities,
        ) = resolve_location_form(
            form,
            organisation_id=organisation.id,
            locations=locations,
            location_types=location_types,
            capabilities=capabilities,
            current_location=None,
            is_primary=is_primary,
        )

    if (
        base_valid
        and references_valid
        and location_type is not None
    ):
        location = OrganisationLocation(
            organisation=organisation,
            is_primary=is_primary,
            is_active=True,
        )

        apply_location_form(
            location,
            form=form,
            location_type=location_type,
            parent=parent,
            capabilities=selected_capabilities,
            is_primary=is_primary,
        )

        db.session.add(location)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(
                "The location could not be created. "
                "Check that its code is unique.",
                "danger",
            )
        else:
            clear_current_organisation()

            flash(
                "Location created successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "org.settings.location_index",
                    selected=location.id,
                )
            )

    return render_template(
        "org/settings/locations/form.html",
        form=form,
        organisation=organisation,
        location=None,
        is_primary=is_primary,
        location_types=location_types,
        capabilities=capabilities,
        location_type_data=build_location_type_data(
            location_types
        ),
        active_org_section="settings",
    )


@settings_bp.route(
    "/locations/<uuid:location_id>/edit",
    methods=["GET", "POST"],
)
@permission_required("org:manage")
def location_edit(location_id: uuid.UUID):
    seed_result = ensure_default_location_catalogue()

    if seed_result.changed:
        current_app.logger.info(
            "Created %s location capabilities and %s location types.",
            seed_result.capabilities_created,
            seed_result.location_types_created,
        )

    organisation = require_current_organisation()
    locations = load_locations(organisation.id)

    location = get_location_or_404(
        organisation.id,
        location_id,
    )

    location_types = load_location_types()
    capabilities = load_capabilities()

    form = LocationForm()

    configure_location_form(
        form,
        locations=locations,
        location_types=location_types,
        capabilities=capabilities,
        current_location=location,
    )

    if not form.is_submitted():
        form.name.data = location.name
        form.code.data = location.code
        form.description.data = location.description
        form.location_type_id.data = str(
            location.location_type_id
        )
        form.parent_id.data = (
            str(location.parent_id)
            if location.parent_id
            else ""
        )
        form.capability_ids.data = [
            str(capability.id)
            for capability in location.capabilities
        ]
        form.sort_order.data = location.sort_order
        form.has_own_address.data = (
            location.has_own_address
        )
        form.address_line_1.data = (
            location.address_line_1
        )
        form.address_line_2.data = (
            location.address_line_2
        )
        form.address_line_3.data = (
            location.address_line_3
        )
        form.town_city.data = location.town_city
        form.county_region.data = (
            location.county_region
        )
        form.postcode.data = location.postcode
        form.country_code.data = (
            location.country_code
        )
        form.phone.data = location.phone
        form.email.data = location.email

    base_valid = form.validate_on_submit()

    references_valid = False
    location_type = None
    parent = None
    selected_capabilities = []

    if form.is_submitted():
        (
            references_valid,
            location_type,
            parent,
            selected_capabilities,
        ) = resolve_location_form(
            form,
            organisation_id=organisation.id,
            locations=locations,
            location_types=location_types,
            capabilities=capabilities,
            current_location=location,
            is_primary=location.is_primary,
        )

    if (
        base_valid
        and references_valid
        and location_type is not None
    ):
        apply_location_form(
            location,
            form=form,
            location_type=location_type,
            parent=parent,
            capabilities=selected_capabilities,
            is_primary=location.is_primary,
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(
                "The location could not be saved. "
                "Check that its code is unique.",
                "danger",
            )
        else:
            clear_current_organisation()

            flash(
                "Location updated successfully.",
                "success",
            )

            return redirect(
                url_for(
                    "org.settings.location_index",
                    selected=location.id,
                )
            )

    return render_template(
        "org/settings/locations/form.html",
        form=form,
        organisation=organisation,
        location=location,
        is_primary=location.is_primary,
        location_types=location_types,
        capabilities=capabilities,
        location_type_data=build_location_type_data(
            location_types
        ),
        active_org_section="settings",
    )


@settings_bp.post(
    "/locations/<uuid:location_id>/deactivate"
)
@permission_required("org:manage")
def location_deactivate(location_id: uuid.UUID):
    organisation = require_current_organisation()
    form = LocationActionForm()

    if not form.validate_on_submit():
        abort(400)

    location = get_location_or_404(
        organisation.id,
        location_id,
    )

    if location.is_primary:
        flash(
            "The primary location cannot be deactivated.",
            "danger",
        )
    elif any(
        child.is_active
        for child in location.children
    ):
        flash(
            "Deactivate or move the active child locations first.",
            "danger",
        )
    else:
        location.is_active = False
        db.session.commit()
        clear_current_organisation()

        flash(
            "Location deactivated.",
            "success",
        )

    return redirect(
        url_for(
            "org.settings.location_index",
            selected=location.id,
        )
    )


@settings_bp.post(
    "/locations/<uuid:location_id>/activate"
)
@permission_required("org:manage")
def location_activate(location_id: uuid.UUID):
    organisation = require_current_organisation()
    form = LocationActionForm()

    if not form.validate_on_submit():
        abort(400)

    location = get_location_or_404(
        organisation.id,
        location_id,
    )

    if (
        location.parent is not None
        and not location.parent.is_active
    ):
        flash(
            "Activate the parent location first.",
            "danger",
        )
    elif not location.location_type.is_active:
        flash(
            "The location type is inactive.",
            "danger",
        )
    else:
        location.is_active = True
        db.session.commit()
        clear_current_organisation()

        flash(
            "Location activated.",
            "success",
        )

    return redirect(
        url_for(
            "org.settings.location_index",
            selected=location.id,
        )
    )