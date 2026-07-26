from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    Optional,
    URL,
)


LOCATION_TYPE_CHOICES = [
    ("registered_office", "Registered office"),
    ("head_office", "Head office"),
    ("operational_base", "Operational base"),
    ("ambulance_station", "Ambulance station"),
    ("warehouse", "Warehouse"),
    ("training_centre", "Training centre"),
    ("other", "Other"),
]


class OrganisationSettingsForm(FlaskForm):
    # Organisation identity
    name = StringField(
        "Organisation name",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    legal_name = StringField(
        "Legal name",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    service_type = StringField(
        "Service type",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    provider_reference = StringField(
        "CQC Registration No.",
        validators=[
            Optional(),
            Length(max=120),
        ],
    )

    company_number = StringField(
        "Company number",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    charity_number = StringField(
        "Charity number",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    vat_number = StringField(
        "VAT number",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    # Contact details
    general_email = StringField(
        "General email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),
        ],
    )

    general_phone = StringField(
        "General telephone",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    website_url = StringField(
        "Website",
        validators=[
            Optional(),
            URL(),
            Length(max=500),
        ],
    )

    region = StringField(
        "Operating region",
        validators=[
            Optional(),
            Length(max=120),
        ],
    )

    
    # Regional defaults
    country_code = StringField(
        "Default country code",
        validators=[
            DataRequired(),
            Length(min=2, max=2),
        ],
    )

    timezone = StringField(
        "Timezone",
        validators=[
            DataRequired(),
            Length(max=64),
        ],
    )

    locale = StringField(
        "Locale",
        validators=[
            DataRequired(),
            Length(max=20),
        ],
    )

    submit = SubmitField("Save settings")