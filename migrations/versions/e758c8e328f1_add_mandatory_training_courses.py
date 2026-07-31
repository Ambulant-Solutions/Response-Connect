"""Add mandatory training courses.

Revision ID: e758c8e328f1
Revises: c2e8a7b4d9f1
"""

from alembic import op
import sqlalchemy as sa


revision = "e758c8e328f1"
down_revision = "c2e8a7b4d9f1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "mandatory_training_courses",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=160),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            server_default=sa.text("''"),
            nullable=False,
        ),
        sa.Column(
            "requalification_period_years",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "sort_order",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "requalification_period_years >= 1",
            name=op.f(
                "ck_mandatory_training_courses_"
                "requalification_period_years_positive"
            ),
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f(
                "pk_mandatory_training_courses"
            ),
        ),
        sa.UniqueConstraint(
            "name",
            name=op.f(
                "uq_mandatory_training_courses_name"
            ),
        ),
    )


def downgrade():
    op.drop_table("mandatory_training_courses")