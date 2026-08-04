from __future__ import annotations

from flask import render_template, url_for

from flask_login import current_user

from app.blueprints.auth import any_permission_required
from app.blueprints.org.services import require_current_organisation
from app.blueprints.org.settings import settings_bp


@settings_bp.get("/", strict_slashes=False)
@any_permission_required(
    "org:manage",
    "auth:manage_users",
    "hr:configure",
)
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
                    "title": "Location types",
                    "description": (
                        "Control the types of sites, departments, rooms, "
                        "cupboards and storage locations that may be created."
                    ),
                    "icon": "tabler:category",
                    "url": url_for(
                        "org.settings.location_type_index"
                    ),
                    "status": "Available",
                    "status_style": "available",
                    "meta": "Location hierarchy",
                },
                {
                    "title": "Locations",
                    "description": (
                        "Manage sites, departments, rooms, cupboards "
                        "and storage locations."
                    ),
                    "icon": "tabler:map-pin",
                    "url": url_for(
                        "org.settings.location_index"
                    ),
                    "status": "Available",
                    "status_style": "available",
                    "meta": (
                        f"{active_location_count} active "
                        f"{'location' if active_location_count == 1 else 'locations'}"
                    ),
                },
                {
                    "title": "UI component showcase",
                    "description": (
                        "Review the reusable administration interface "
                        "components and interaction patterns."
                    ),
                    "icon": "tabler:components",
                    "url": url_for(
                        "org.settings.component_showcase"
                    ),
                    "status": "Development",
                    "status_style": "next",
                    "meta": "Internal style guide",
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
                    "title": "Job positions",
                    "description": (
                        "Define the organisational positions that may "
                        "be assigned to staff members."
                    ),
                    "icon": "tabler:briefcase",
                    "url": url_for(
                        "org.settings.job_position_index"
                    ),
                    "status": "Available",
                    "status_style": "available",
                    "meta": "Organisational structure",
                    "permission": "hr:configure",
                },
                {
                    "title": "Clinical grades",
                    "description": (
                        "Configure clinical grades and operational "
                        "clinical levels."
                    ),
                    "icon": "tabler:stethoscope",
                    "url": None,
                    "status": "Next",
                    "status_style": "next",
                    "meta": "Clinical workforce",
                    "permission": "hr:configure",
                },
                {
                    "title": "Mandatory training courses",
                    "description": (
                        "Configure mandatory training courses and "
                        "their requalification periods."
                    ),
                    "icon": "tabler:school",
                    "url": url_for(
                        "org.settings."
                        "mandatory_training_course_index"
                    ),
                    "status": "Available",
                    "status_style": "available",
                    "meta": "Training compliance",
                    "permission": "hr:manage_training",
                },
                {
                    "title": "Employment statuses",
                    "description": (
                        "Configure the employment states available "
                        "for staff records."
                    ),
                    "icon": "tabler:user-cog",
                    "url": None,
                    "status": "Planned",
                    "status_style": "planned",
                    "meta": "Employment records",
                    "permission": "hr:configure",
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
                    "permission": "hr:configure",
                },
                {
                    "title": "Roles and permissions",
                    "description": (
                        "Control administrative roles and access to "
                        "organisation functions."
                    ),
                    "icon": "tabler:user-shield",
                    "url": url_for(
                        "org.settings.role_index"
                    ),
                    "status": "Available",
                    "status_style": "available",
                    "meta": "Access control",
                    "permission": "auth:manage_users",
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

    visible_sections = []

    for section in settings_sections:
        visible_items = [
            item
            for item in section["items"]
            if current_user.has_permission(
                item.get(
                    "permission",
                    "org:manage",
                )
            )
        ]

        if visible_items:
            visible_sections.append(
                {
                    **section,
                    "items": visible_items,
                }
            )

    settings_sections = visible_sections

    return render_template(
        "org/settings/index.html",
        organisation=organisation,
        settings_sections=settings_sections,
        active_org_section="settings",
    )

@settings_bp.get(
    "/dev/components",
    strict_slashes=False,
)
@any_permission_required(
    "org:manage",
)
def component_showcase():
    """Display the internal administration UI component showcase."""

    organisation = require_current_organisation()

    sample_timeline = [
        {
            "icon": "tabler:plus",
            "style": "success",
            "title": "Desk created",
            "summary": (
                "Desk 'Operations Control' was created."
            ),
            "actor": "System Administrator",
            "occurred_at": "Today at 09:12",
        },
        {
            "icon": "tabler:pencil",
            "style": "info",
            "title": "Desk updated",
            "summary": (
                "The Desk name and description were updated."
            ),
            "actor": "Kieran Smith",
            "occurred_at": "Today at 09:24",
            "changes": [
                {
                    "label": "Name",
                    "previous": "Operations",
                    "current": "Operations Control",
                },
                {
                    "label": "Description",
                    "previous": "Operational services.",
                    "current": (
                        "Organisation-wide command and control."
                    ),
                },
            ],
        },
        {
            "icon": "tabler:arrows-move",
            "style": "warning",
            "title": "Desk moved",
            "summary": (
                "Desk 'Event Operations' was moved."
            ),
            "actor": "Kieran Smith",
            "occurred_at": "Yesterday at 16:40",
            "changes": [
                {
                    "label": "Parent Desk",
                    "previous": "Organisation",
                    "current": "Operations Control",
                },
            ],
        },
    ]

    sample_tree = [
        {
            "name": organisation.name,
            "icon": "tabler:building",
            "status": "Active",
            "status_style": "active",
            "selected": False,
            "children": [
                {
                    "name": "Operations Control",
                    "icon": "tabler:headset",
                    "status": "Active",
                    "status_style": "active",
                    "selected": True,
                    "children": [
                        {
                            "name": "Event Operations",
                            "icon": "tabler:building-circus",
                            "status": "Active",
                            "status_style": "active",
                            "selected": False,
                            "children": [],
                        },
                        {
                            "name": "Patient Transport",
                            "icon": "tabler:ambulance",
                            "status": "Inactive",
                            "status_style": "inactive",
                            "selected": False,
                            "children": [],
                        },
                    ],
                },
                {
                    "name": "Clinical Governance",
                    "icon": "tabler:stethoscope",
                    "status": "Active",
                    "status_style": "active",
                    "selected": False,
                    "children": [],
                },
                {
                    "name": "Archived Desk",
                    "icon": "tabler:archive",
                    "status": "Archived",
                    "status_style": "archived",
                    "selected": False,
                    "children": [],
                },
            ],
        },
    ]

    return render_template(
        "org/settings/dev/components.html",
        organisation=organisation,
        sample_tree=sample_tree,
        sample_timeline=sample_timeline,
        active_org_section="settings",
    )