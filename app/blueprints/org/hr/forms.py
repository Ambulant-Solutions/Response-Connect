from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    InputRequired,
    Length,
    NumberRange,
    Optional,
)


class JobPositionForm(FlaskForm):
    name = StringField(
        "Position name",
        validators=[
            DataRequired(),
            Length(max=160),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Optional(),
            Length(max=2000),
        ],
    )

    sort_order = IntegerField(
        "Display order",
        validators=[
            InputRequired(),
            NumberRange(min=0, max=9999),
        ],
        default=0,
    )

    submit = SubmitField("Save position")


class JobPositionActionForm(FlaskForm):
    submit = SubmitField("Confirm")