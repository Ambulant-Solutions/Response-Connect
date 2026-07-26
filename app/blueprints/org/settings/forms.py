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

    # Primary location
    location_name = StringField(
        "Location name",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    location_type = SelectField(
        "Location type",
        choices=LOCATION_TYPE_CHOICES,
        validators=[DataRequired()],
    )

    address_line_1 = StringField(
        "Address line 1",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    address_line_2 = StringField(
        "Address line 2",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    address_line_3 = StringField(
        "Address line 3",
        validators=[
            Optional(),
            Length(max=255),
        ],
    )

    town_city = StringField(
        "Town or city",
        validators=[
            DataRequired(),
            Length(max=120),
        ],
    )

    county_region = StringField(
        "County or region",
        validators=[
            Optional(),
            Length(max=120),
        ],
    )

    postcode = StringField(
        "Postcode",
        validators=[
            Optional(),
            Length(max=20),
        ],
    )

    location_country_code = StringField(
        "Location country code",
        validators=[
            DataRequired(),
            Length(min=2, max=2),
        ],
    )

    location_phone = StringField(
        "Location telephone",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    location_email = StringField(
        "Location email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),
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