from __future__ import annotations

from flask import render_template, url_for

from app.blueprints.auth import permission_required
from app.blueprints.org.services import require_current_organisation
from app.blueprints.org.settings import settings_bp


@settings_bp.get("/", strict_slashes=False)
@permission_required("org:manage")
def index():
    organisation = require_current_organisation()

    active_location_count = sum(
        1
        for location in organisation.locations
        if location.is_active
    )

    settings_sections = [
        {
            "id": "general",
            "title": "General",
            "description": (
                "Organisation identity, locations and system-wide defaults."
            ),
            "items": [
                {
                    "title": "Organisation profile",
                    "description": (
                        "Manage the organisation name, legal identity, "
                        "contact details and regional defaults."
                    ),
                    "icon": "tabler:building",
                    "url": url_for(
                        "org.settings.organisation"
                    ),
                    "status": "Available",
                    "status_style": "available",
                    "meta": "Organisation-wide",
                },
                {
                    "title": "Locations",
                    "description": (
                        "Manage registered offices, operational bases, "
                        "ambulance stations, warehouses and training centres."
                    ),
                    "icon": "tabler:map-pin",
                    "url": None,
                    "status": "Next",
                    "status_style": "next",
                    "meta": (
                        f"{active_location_count} active "
                        f"{'location' if active_location_count == 1 else 'locations'}"
                    ),
                },
            ],
        },
        {
            "id": "workforce",
            "title": "Workforce",
            "description": (
                "Settings used when managing staff, access and competency."
            ),
            "items": [
                {
                    "title": "Roles and permissions",
                    "description": (
                        "Control administrative roles and access to "
                        "organisation functions."
                    ),
                    "icon": "tabler:user-shield",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Access control",
                },
                {
                    "title": "Staff grades",
                    "description": (
                        "Configure clinical grades, operational roles "
                        "and staff classifications."
                    ),
                    "icon": "tabler:users-group",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "HR and scheduling",
                },
                {
                    "title": "Qualifications and competencies",
                    "description": (
                        "Manage recognised qualifications, competencies "
                        "and compliance requirements."
                    ),
                    "icon": "tabler:certificate",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Training and compliance",
                },
            ],
        },
        {
            "id": "operations",
            "title": "Operations",
            "description": (
                "Configure the classifications used for operational work."
            ),
            "items": [
                {
                    "title": "Shift and duty types",
                    "description": (
                        "Define shift types, duty categories and "
                        "operational working patterns."
                    ),
                    "icon": "tabler:calendar-clock",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Scheduling",
                },
                {
                    "title": "Event types",
                    "description": (
                        "Configure categories for events, deployments "
                        "and planned medical cover."
                    ),
                    "icon": "tabler:building-circus",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Events",
                },
                {
                    "title": "Incident categories",
                    "description": (
                        "Manage incident classifications, priorities "
                        "and reportable incident types."
                    ),
                    "icon": "tabler:alert-triangle",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Incidents",
                },
            ],
        },
        {
            "id": "fleet-assets",
            "title": "Fleet and assets",
            "description": (
                "Settings used for vehicles, equipment and stock control."
            ),
            "items": [
                {
                    "title": "Vehicle types",
                    "description": (
                        "Define ambulance, response, transport and "
                        "support vehicle classifications."
                    ),
                    "icon": "tabler:ambulance",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Fleet",
                },
                {
                    "title": "Vehicle statuses",
                    "description": (
                        "Configure operational, unavailable, maintenance "
                        "and other fleet statuses."
                    ),
                    "icon": "tabler:traffic-cone",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Fleet availability",
                },
                {
                    "title": "Stock categories and units",
                    "description": (
                        "Manage stock classifications, units of measure "
                        "and storage categories."
                    ),
                    "icon": "tabler:packages",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Stock control",
                },
            ],
        },
        {
            "id": "clinical",
            "title": "Clinical records",
            "description": (
                "Configure lists and classifications used in clinical records."
            ),
            "items": [
                {
                    "title": "Presenting complaints",
                    "description": (
                        "Manage the presenting complaint options used "
                        "when creating patient records."
                    ),
                    "icon": "tabler:stethoscope",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "ePCR",
                },
                {
                    "title": "Patient outcomes",
                    "description": (
                        "Configure treatment, discharge, referral and "
                        "transport outcomes."
                    ),
                    "icon": "tabler:clipboard-heart",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "ePCR",
                },
                {
                    "title": "Medication catalogue",
                    "description": (
                        "Manage medications, preparations, routes and "
                        "administration defaults."
                    ),
                    "icon": "tabler:pill",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Medications",
                },
            ],
        },
    ]

    return render_template(
        "org/settings/index.html",
        organisation=organisation,
        settings_sections=settings_sections,
        active_org_section="settings",
    )