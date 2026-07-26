from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    URL,
)
from wtforms.widgets import CheckboxInput, ListWidget


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

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class LocationForm(FlaskForm):
    name = StringField(
        "Location name",
        validators=[
            DataRequired(),
            Length(max=255),
        ],
    )

    code = StringField(
        "Location code",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000),
        ],
    )

    location_type_id = SelectField(
        "Location type",
        validators=[DataRequired()],
    )

    parent_id = SelectField(
        "Parent location",
        validators=[Optional()],
    )

    capability_ids = MultiCheckboxField(
        "Permitted uses",
        validators=[Optional()],
    )

    sort_order = IntegerField(
        "Display order",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=9999),
        ],
        default=0,
    )

    has_own_address = BooleanField(
        "This location has its own postal address"
    )

    address_line_1 = StringField(
        "Address line 1",
        validators=[
            Optional(),
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
            Optional(),
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

    country_code = StringField(
        "Country code",
        validators=[
            DataRequired(),
            Length(min=2, max=2),
        ],
        default="GB",
    )

    phone = StringField(
        "Telephone",
        validators=[
            Optional(),
            Length(max=50),
        ],
    )

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(),
            Length(max=255),
        ],
    )

    submit = SubmitField("Save location")

class LocationTypeForm(FlaskForm):
    code = StringField(
        "Type code",
        validators=[
            DataRequired(),
            Length(max=64),
        ],
    )

    name = StringField(
        "Type name",
        validators=[
            DataRequired(),
            Length(max=120),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=500),
        ],
    )

    icon = StringField(
        "Icon",
        validators=[
            DataRequired(),
            Length(max=120),
        ],
        default="tabler:map-pin",
    )

    is_physical = BooleanField(
        "This represents a physical place"
    )

    can_have_children = BooleanField(
        "Locations of this type may contain child locations"
    )

    requires_address = BooleanField(
        "Locations of this type require their own postal address"
    )

    capability_ids = MultiCheckboxField(
        "Maximum permitted uses",
        validators=[Optional()],
    )

    sort_order = IntegerField(
        "Display order",
        validators=[
            DataRequired(),
            NumberRange(min=0, max=9999),
        ],
        default=0,
    )

    submit = SubmitField("Save location type")


class LocationActionForm(FlaskForm):
    submit = SubmitField("Confirm")


class LocationTypeActionForm(FlaskForm):
    submit = SubmitField("Confirm")