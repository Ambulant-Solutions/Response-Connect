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

    form = OrganisationSettingsForm()

    if not form.is_submitted():
        populate_form(
            form=form,
            organisation=organisation
        )

    if form.validate_on_submit():
        update_organisation(
            organisation=organisation,
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


