"""Add HR positions and clinical grades.

Revision ID: c2e8a7b4d9f1
Revises: f14b27c8d93a
"""

from alembic import op
import sqlalchemy as sa


revision = "c2e8a7b4d9f1"
down_revision = "f14b27c8d93a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "job_positions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column(
            "description",
            sa.Text(),
            server_default=sa.text("''"),
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
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_job_positions"),
        ),
        sa.UniqueConstraint(
            "name",
            name=op.f("uq_job_positions_name"),
        ),
    )

    op.create_table(
        "clinical_grades",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column(
            "abbreviation",
            sa.String(length=40),
            server_default=sa.text("''"),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            server_default=sa.text("''"),
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
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_clinical_grades"),
        ),
        sa.UniqueConstraint(
            "name",
            name=op.f("uq_clinical_grades_name"),
        ),
    )

    op.create_table(
        "staff_position_assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("staff_member_id", sa.UUID(), nullable=False),
        sa.Column("position_id", sa.UUID(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "is_primary",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            server_default=sa.text("''"),
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
            "end_date IS NULL OR end_date >= start_date",
            name=op.f(
                "ck_staff_position_assignments_date_order"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["position_id"],
            ["job_positions.id"],
            name=op.f(
                "fk_staff_position_assignments_"
                "position_id_job_positions"
            ),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["staff_member_id"],
            ["staff_members.id"],
            name=op.f(
                "fk_staff_position_assignments_"
                "staff_member_id_staff_members"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_staff_position_assignments"),
        ),
    )

    op.create_index(
        op.f(
            "ix_staff_position_assignments_staff_member_id"
        ),
        "staff_position_assignments",
        ["staff_member_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_staff_position_assignments_position_id"),
        "staff_position_assignments",
        ["position_id"],
        unique=False,
    )

    op.create_table(
        "staff_clinical_grade_assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("staff_member_id", sa.UUID(), nullable=False),
        sa.Column("clinical_grade_id", sa.UUID(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "is_primary",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.Text(),
            server_default=sa.text("''"),
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
            "end_date IS NULL OR end_date >= start_date",
            name=op.f(
                "ck_staff_clinical_grade_assignments_date_order"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["clinical_grade_id"],
            ["clinical_grades.id"],
            name=op.f(
                "fk_staff_clinical_grade_assignments_"
                "clinical_grade_id_clinical_grades"
            ),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["staff_member_id"],
            ["staff_members.id"],
            name=op.f(
                "fk_staff_clinical_grade_assignments_"
                "staff_member_id_staff_members"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f(
                "pk_staff_clinical_grade_assignments"
            ),
        ),
    )

    op.create_index(
        op.f(
            "ix_staff_clinical_grade_assignments_"
            "staff_member_id"
        ),
        "staff_clinical_grade_assignments",
        ["staff_member_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_staff_clinical_grade_assignments_"
            "clinical_grade_id"
        ),
        "staff_clinical_grade_assignments",
        ["clinical_grade_id"],
        unique=False,
    )


def downgrade():
    op.drop_index(
        op.f(
            "ix_staff_clinical_grade_assignments_"
            "clinical_grade_id"
        ),
        table_name="staff_clinical_grade_assignments",
    )

    op.drop_index(
        op.f(
            "ix_staff_clinical_grade_assignments_"
            "staff_member_id"
        ),
        table_name="staff_clinical_grade_assignments",
    )

    op.drop_table("staff_clinical_grade_assignments")

    op.drop_index(
        op.f("ix_staff_position_assignments_position_id"),
        table_name="staff_position_assignments",
    )

    op.drop_index(
        op.f(
            "ix_staff_position_assignments_staff_member_id"
        ),
        table_name="staff_position_assignments",
    )

    op.drop_table("staff_position_assignments")
    op.drop_table("clinical_grades")
    op.drop_table("job_positions")