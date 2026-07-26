from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from app.blueprints.org.models import (
    LocationCapability,
    LocationType,
)
from app.extensions import db


DEFAULT_LOCATION_CAPABILITIES = (
    {
        "code": "staff_base",
        "name": "Staff base",
        "description": (
            "Staff members and organisational teams may be based "
            "at this location."
        ),
        "icon": "tabler:users",
        "sort_order": 10,
    },
    {
        "code": "vehicle_base",
        "name": "Vehicle base",
        "description": (
            "Vehicles may be based, parked or assigned to this location."
        ),
        "icon": "tabler:ambulance",
        "sort_order": 20,
    },
    {
        "code": "stock_storage",
        "name": "Stock storage",
        "description": (
            "General consumable stock may be held at this location."
        ),
        "icon": "tabler:packages",
        "sort_order": 30,
    },
    {
        "code": "equipment_storage",
        "name": "Equipment storage",
        "description": (
            "Reusable equipment and operational assets may be held here."
        ),
        "icon": "tabler:tool",
        "sort_order": 40,
    },
    {
        "code": "medication_storage",
        "name": "Medication storage",
        "description": (
            "Medicines may be stored at this location, subject to "
            "the appropriate medicines controls."
        ),
        "icon": "tabler:pill",
        "sort_order": 50,
    },
    {
        "code": "controlled_drug_storage",
        "name": "Controlled drug storage",
        "description": (
            "Controlled drugs may be stored at this location."
        ),
        "icon": "tabler:lock",
        "sort_order": 60,
    },
    {
        "code": "document_storage",
        "name": "Document storage",
        "description": (
            "Physical records and organisational documents may be "
            "held at this location."
        ),
        "icon": "tabler:files",
        "sort_order": 70,
    },
)


DEFAULT_LOCATION_TYPES = (
    {
        "code": "head_office",
        "name": "Head office",
        "description": (
            "The organisation's principal administrative location."
        ),
        "icon": "tabler:building",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": True,
        "sort_order": 10,
        "capabilities": (
            "staff_base",
            "vehicle_base",
            "stock_storage",
            "equipment_storage",
            "medication_storage",
            "document_storage",
        ),
    },
    {
        "code": "operational_base",
        "name": "Operational base",
        "description": (
            "A base from which operational teams and resources work."
        ),
        "icon": "tabler:building-community",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": True,
        "sort_order": 20,
        "capabilities": (
            "staff_base",
            "vehicle_base",
            "stock_storage",
            "equipment_storage",
            "medication_storage",
            "document_storage",
        ),
    },
    {
        "code": "ambulance_station",
        "name": "Ambulance station",
        "description": (
            "An operational station used by ambulance crews and vehicles."
        ),
        "icon": "tabler:ambulance",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": True,
        "sort_order": 30,
        "capabilities": (
            "staff_base",
            "vehicle_base",
            "stock_storage",
            "equipment_storage",
            "medication_storage",
        ),
    },
    {
        "code": "warehouse",
        "name": "Warehouse",
        "description": (
            "A larger location used for stock and equipment storage."
        ),
        "icon": "tabler:building-warehouse",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 40,
        "capabilities": (
            "stock_storage",
            "equipment_storage",
        ),
    },
    {
        "code": "training_centre",
        "name": "Training centre",
        "description": (
            "A location used for education, training and assessment."
        ),
        "icon": "tabler:school",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": True,
        "sort_order": 50,
        "capabilities": (
            "staff_base",
            "stock_storage",
            "equipment_storage",
            "document_storage",
        ),
    },
    {
        "code": "department",
        "name": "Department",
        "description": (
            "An organisational team or department within another location."
        ),
        "icon": "tabler:hierarchy-2",
        "is_physical": False,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 60,
        "capabilities": (
            "staff_base",
            "document_storage",
        ),
    },
    {
        "code": "office",
        "name": "Office",
        "description": "An office or administrative workspace.",
        "icon": "tabler:desk",
        "is_physical": True,
        "can_have_children": False,
        "requires_address": False,
        "sort_order": 70,
        "capabilities": (
            "staff_base",
            "document_storage",
        ),
    },
    {
        "code": "store_room",
        "name": "Store room",
        "description": (
            "A room used for general stock and equipment storage."
        ),
        "icon": "tabler:door",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 80,
        "capabilities": (
            "stock_storage",
            "equipment_storage",
        ),
    },
    {
        "code": "cupboard",
        "name": "Cupboard",
        "description": (
            "A cupboard used for general stock or equipment storage."
        ),
        "icon": "tabler:archive",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 90,
        "capabilities": (
            "stock_storage",
            "equipment_storage",
        ),
    },
    {
        "code": "shelf",
        "name": "Shelf",
        "description": "A shelf or defined stock storage position.",
        "icon": "tabler:layout-rows",
        "is_physical": True,
        "can_have_children": False,
        "requires_address": False,
        "sort_order": 100,
        "capabilities": (
            "stock_storage",
            "equipment_storage",
        ),
    },
    {
        "code": "vehicle_compound",
        "name": "Vehicle compound",
        "description": (
            "An external or internal area used to store vehicles."
        ),
        "icon": "tabler:parking",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 110,
        "capabilities": (
            "vehicle_base",
        ),
    },
    {
        "code": "vehicle_bay",
        "name": "Vehicle bay",
        "description": "An individual parking or vehicle storage bay.",
        "icon": "tabler:parking-circle",
        "is_physical": True,
        "can_have_children": False,
        "requires_address": False,
        "sort_order": 120,
        "capabilities": (
            "vehicle_base",
        ),
    },
    {
        "code": "medication_room",
        "name": "Medication room",
        "description": (
            "A secured room containing medication storage locations."
        ),
        "icon": "tabler:first-aid-kit",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 130,
        "capabilities": (
            "medication_storage",
        ),
    },
    {
        "code": "medication_cupboard",
        "name": "Medication cupboard",
        "description": "A secured cupboard used to store medications.",
        "icon": "tabler:medical-cross",
        "is_physical": True,
        "can_have_children": False,
        "requires_address": False,
        "sort_order": 140,
        "capabilities": (
            "medication_storage",
        ),
    },
    {
        "code": "controlled_drugs_safe",
        "name": "Controlled drugs safe",
        "description": (
            "A secured safe approved for controlled-drug storage."
        ),
        "icon": "tabler:safe",
        "is_physical": True,
        "can_have_children": False,
        "requires_address": False,
        "sort_order": 150,
        "capabilities": (
            "medication_storage",
            "controlled_drug_storage",
        ),
    },
    {
        "code": "medication_fridge",
        "name": "Medication fridge",
        "description": (
            "A temperature-controlled refrigerator used for medicines."
        ),
        "icon": "tabler:fridge",
        "is_physical": True,
        "can_have_children": False,
        "requires_address": False,
        "sort_order": 160,
        "capabilities": (
            "medication_storage",
        ),
    },
    {
        "code": "document_store",
        "name": "Document store",
        "description": (
            "A secured location used for physical records and documents."
        ),
        "icon": "tabler:archive",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 170,
        "capabilities": (
            "document_storage",
        ),
    },
    {
        "code": "other",
        "name": "Other",
        "description": (
            "A general location type which may be configured as required."
        ),
        "icon": "tabler:map-pin",
        "is_physical": True,
        "can_have_children": True,
        "requires_address": False,
        "sort_order": 999,
        "capabilities": (),
    },
)


@dataclass(frozen=True)
class LocationCatalogueSeedResult:
    capabilities_created: int
    location_types_created: int

    @property
    def changed(self) -> bool:
        return (
            self.capabilities_created > 0
            or self.location_types_created > 0
        )


def ensure_default_location_catalogue(
) -> LocationCatalogueSeedResult:
    """
    Create missing standard capabilities and location types.

    Existing records are deliberately left unchanged so administrator
    amendments, disabled records and capability selections are preserved.
    """

    capabilities_created = 0
    location_types_created = 0

    existing_capabilities = {
        capability.code: capability
        for capability in db.session.scalars(
            select(LocationCapability)
        ).all()
    }

    for definition in DEFAULT_LOCATION_CAPABILITIES:
        code = definition["code"]

        if code in existing_capabilities:
            continue

        capability = LocationCapability(
            code=code,
            name=definition["name"],
            description=definition["description"],
            icon=definition["icon"],
            sort_order=definition["sort_order"],
            is_active=True,
        )

        db.session.add(capability)
        existing_capabilities[code] = capability
        capabilities_created += 1

    # Ensure newly created capabilities have been inserted before they
    # are assigned through the many-to-many relationship.
    db.session.flush()

    existing_location_types = {
        location_type.code: location_type
        for location_type in db.session.scalars(
            select(LocationType)
        ).all()
    }

    for definition in DEFAULT_LOCATION_TYPES:
        code = definition["code"]

        if code in existing_location_types:
            continue

        location_type = LocationType(
            code=code,
            name=definition["name"],
            description=definition["description"],
            icon=definition["icon"],
            is_physical=definition["is_physical"],
            can_have_children=definition["can_have_children"],
            requires_address=definition["requires_address"],
            is_system=True,
            is_active=True,
            sort_order=definition["sort_order"],
        )

        location_type.allowed_capabilities = [
            existing_capabilities[capability_code]
            for capability_code in definition["capabilities"]
        ]

        db.session.add(location_type)
        existing_location_types[code] = location_type
        location_types_created += 1

    if capabilities_created or location_types_created:
        db.session.commit()

    return LocationCatalogueSeedResult(
        capabilities_created=capabilities_created,
        location_types_created=location_types_created,
    )