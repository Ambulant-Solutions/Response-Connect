from __future__ import annotations

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    url_for,
)
from sqlalchemy.exc import IntegrityError
from app.blueprints.org.settings import settings_bp
from app.blueprints.auth import permission_required
from app.blueprints.org.settings.forms import OrganisationSettingsForm
from app.blueprints.org.models import OrganisationLocation
from app.blueprints.org.services import (
    clear_current_organisation,
    require_current_organisation,
)
from app.extensions import db



def optional_text(value: str | None) -> str | None:
    """Convert an empty optional form field to None."""

    if value is None:
        return None

    cleaned_value = value.strip()
    return cleaned_value or None


@settings_bp.route(
    "/organisation",
    methods=["GET", "POST"],
    strict_slashes=False,
)
@permission_required("org:manage")
def organisation():
    organisation = require_current_organisation()
    location = organisation.primary_location_record

    form = OrganisationSettingsForm()

    if not form.is_submitted():
        populate_form(
            form=form,
            organisation=organisation,
            location=location,
        )

    if form.validate_on_submit():
        update_organisation(
            organisation=organisation,
            form=form,
        )

        if location is None:
            location = OrganisationLocation(
                organisation=organisation,
                is_primary=True,
                is_active=True,
            )
            db.session.add(location)

        update_location(
            location=location,
            form=form,
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The organisation settings could not be saved. "
                "A company number, provider reference or other "
                "unique identifier may already be in use.",
                "danger",
            )
        else:
            clear_current_organisation()

            flash(
                "Organisation settings saved successfully.",
                "success",
            )

            return redirect(
                url_for("org.settings.organisation")
            )

    return render_template(
        "org/settings/organisation_settings.html",
        form=form,
        organisation=organisation,
        active_org_section="settings",
    )


def populate_form(
    *,
    form: OrganisationSettingsForm,
    organisation,
    location: OrganisationLocation | None,
) -> None:
    """Populate the form for its initial GET request."""

    form.name.data = organisation.name
    form.legal_name.data = organisation.legal_name
    form.service_type.data = organisation.service_type
    form.provider_reference.data = organisation.provider_reference
    form.company_number.data = organisation.company_number
    form.charity_number.data = organisation.charity_number
    form.vat_number.data = organisation.vat_number

    form.general_email.data = organisation.general_email
    form.general_phone.data = organisation.general_phone
    form.website_url.data = organisation.website_url
    form.region.data = organisation.region

    form.country_code.data = organisation.country_code
    form.timezone.data = organisation.timezone
    form.locale.data = organisation.locale

    if location is None:
        form.location_name.data = "Primary location"
        form.location_type.data = "registered_office"
        form.location_country_code.data = (
            organisation.country_code
        )
        return

    form.location_name.data = location.name
    form.location_type.data = location.location_type
    form.address_line_1.data = location.address_line_1
    form.address_line_2.data = location.address_line_2
    form.address_line_3.data = location.address_line_3
    form.town_city.data = location.town_city
    form.county_region.data = location.county_region
    form.postcode.data = location.postcode
    form.location_country_code.data = location.country_code
    form.location_phone.data = location.phone
    form.location_email.data = location.email


def update_organisation(
    *,
    organisation,
    form: OrganisationSettingsForm,
) -> None:
    organisation.name = form.name.data.strip()
    organisation.legal_name = optional_text(
        form.legal_name.data
    )
    organisation.service_type = optional_text(
        form.service_type.data
    )
    organisation.provider_reference = optional_text(
        form.provider_reference.data
    )
    organisation.company_number = optional_text(
        form.company_number.data
    )
    organisation.charity_number = optional_text(
        form.charity_number.data
    )
    organisation.vat_number = optional_text(
        form.vat_number.data
    )

    organisation.general_email = optional_text(
        form.general_email.data
    )
    if organisation.general_email:
        organisation.general_email = (
            organisation.general_email.lower()
        )

    organisation.general_phone = optional_text(
        form.general_phone.data
    )
    organisation.website_url = optional_text(
        form.website_url.data
    )
    organisation.region = optional_text(
        form.region.data
    )

    organisation.country_code = (
        form.country_code.data.strip().upper()
    )
    organisation.timezone = form.timezone.data.strip()
    organisation.locale = form.locale.data.strip()


def update_location(
    *,
    location: OrganisationLocation,
    form: OrganisationSettingsForm,
) -> None:
    location.name = form.location_name.data.strip()
    location.location_type = form.location_type.data

    location.address_line_1 = (
        form.address_line_1.data.strip()
    )
    location.address_line_2 = optional_text(
        form.address_line_2.data
    )
    location.address_line_3 = optional_text(
        form.address_line_3.data
    )
    location.town_city = form.town_city.data.strip()
    location.county_region = optional_text(
        form.county_region.data
    )
    location.postcode = optional_text(
        form.postcode.data
    )

    if location.postcode:
        location.postcode = location.postcode.upper()

    location.country_code = (
        form.location_country_code.data.strip().upper()
    )
    location.phone = optional_text(
        form.location_phone.data
    )
    location.email = optional_text(
        form.location_email.data
    )

    if location.email:
        location.email = location.email.lower()

    location.is_primary = True
    location.is_active = True