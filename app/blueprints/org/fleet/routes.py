from app.blueprints.org.fleet import fleet_bp  # noqa: F401
from flask import Blueprint, jsonify, render_template, url_for

@fleet_bp.get("/")
def fleet():
    return render_template(
        "org/not_implemented.html",
        active_org_section="fleet",
        section_title="Vehicle management",
        section_eyebrow="Fleet administration",
        section_icon="tabler:ambulance",
        section_description=(
            "Vehicle management is planned but is not yet available "
            "in this version of Response Connect."
        ),
        release_note=(
            "This section is currently in active development. "
            "No release date has been assigned."
        ),
        planned_features=[
            "Vehicle and fleet records",
            "Daily readiness checks",
            "Defect reporting and resolution",
            "Maintenance and servicing history",
            "Insurance and compliance documents",
            "Vehicle allocation to operations",
        ],
        return_url=url_for("org.org"),
        return_label="Return to organisation overview",
    )