"""Add people and staff foundation.

Revision ID: f14b27c8d93a
Revises: 99589dceb70e
"""

from __future__ import annotations

import uuid

from alembic import op
import sqlalchemy as sa


revision = "f14b27c8d93a"
down_revision = "99589dceb70e"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # Read names before removing them from the old tables.
    existing_users = list(
        bind.execute(
            sa.text(
                """
                SELECT id, first_name, last_name
                FROM user_accounts
                """
            )
        ).mappings()
    )

    existing_staff = list(
        bind.execute(
            sa.text(
                """
                SELECT id, first_name, last_name
                FROM staff_members
                """
            )
        ).mappings()
    )

    # Create the new shared people table.
    op.create_table(
        "persons",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "first_name",
            sa.String(length=120),
            server_default="",
            nullable=False,
        ),
        sa.Column(
            "middle_names",
            sa.String(length=255),
            server_default="",
            nullable=False,
        ),
        sa.Column(
            "last_name",
            sa.String(length=120),
            server_default="",
            nullable=False,
        ),
        sa.Column(
            "preferred_name",
            sa.String(length=120),
            server_default="",
            nullable=False,
        ),
        sa.PrimaryKeyConstraint(
            "id",
            name=op.f("pk_persons"),
        ),
    )

    persons = sa.table(
        "persons",
        sa.column("id", sa.UUID()),
        sa.column("first_name", sa.String()),
        sa.column("middle_names", sa.String()),
        sa.column("last_name", sa.String()),
        sa.column("preferred_name", sa.String()),
    )

    # Give every existing account and staff record a Person.
    user_person_ids = {
        row["id"]: uuid.uuid4()
        for row in existing_users
    }

    staff_person_ids = {
        row["id"]: uuid.uuid4()
        for row in existing_staff
    }

    person_rows = [
        {
            "id": user_person_ids[row["id"]],
            "first_name": row["first_name"] or "",
            "middle_names": "",
            "last_name": row["last_name"] or "",
            "preferred_name": "",
        }
        for row in existing_users
    ]

    person_rows.extend(
        {
            "id": staff_person_ids[row["id"]],
            "first_name": row["first_name"] or "",
            "middle_names": "",
            "last_name": row["last_name"] or "",
            "preferred_name": "",
        }
        for row in existing_staff
    )

    if person_rows:
        bind.execute(
            persons.insert(),
            person_rows,
        )

    # Connect existing user accounts to their new Person.
    op.add_column(
        "user_accounts",
        sa.Column(
            "person_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    if user_person_ids:
        bind.execute(
            sa.text(
                """
                UPDATE user_accounts
                SET person_id = :person_id
                WHERE id = :record_id
                """
            ),
            [
                {
                    "person_id": person_id,
                    "record_id": user_id,
                }
                for user_id, person_id
                in user_person_ids.items()
            ],
        )

    op.create_foreign_key(
        "fk_user_accounts_person_id_persons",
        "user_accounts",
        "persons",
        ["person_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_unique_constraint(
        "uq_user_accounts_person_id",
        "user_accounts",
        ["person_id"],
    )

    op.alter_column(
        "user_accounts",
        "person_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    op.drop_column(
        "user_accounts",
        "last_name",
    )

    op.drop_column(
        "user_accounts",
        "first_name",
    )

    # Extend and connect existing staff records.
    op.add_column(
        "staff_members",
        sa.Column(
            "person_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    op.add_column(
        "staff_members",
        sa.Column(
            "employment_status",
            sa.String(length=32),
            server_default="active",
            nullable=False,
        ),
    )

    op.add_column(
        "staff_members",
        sa.Column(
            "start_date",
            sa.Date(),
            nullable=True,
        ),
    )

    op.add_column(
        "staff_members",
        sa.Column(
            "leaving_date",
            sa.Date(),
            nullable=True,
        ),
    )

    if staff_person_ids:
        bind.execute(
            sa.text(
                """
                UPDATE staff_members
                SET person_id = :person_id
                WHERE id = :record_id
                """
            ),
            [
                {
                    "person_id": person_id,
                    "record_id": staff_id,
                }
                for staff_id, person_id
                in staff_person_ids.items()
            ],
        )

    op.create_foreign_key(
        "fk_staff_members_person_id_persons",
        "staff_members",
        "persons",
        ["person_id"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_unique_constraint(
        "uq_staff_members_person_id",
        "staff_members",
        ["person_id"],
    )

    op.alter_column(
        "staff_members",
        "person_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    op.drop_column(
        "staff_members",
        "last_name",
    )

    op.drop_column(
        "staff_members",
        "first_name",
    )


def downgrade():
    bind = op.get_bind()

    # Restore the old name columns temporarily as nullable.
    op.add_column(
        "user_accounts",
        sa.Column(
            "first_name",
            sa.String(length=120),
            nullable=True,
        ),
    )

    op.add_column(
        "user_accounts",
        sa.Column(
            "last_name",
            sa.String(length=120),
            nullable=True,
        ),
    )

    op.add_column(
        "staff_members",
        sa.Column(
            "first_name",
            sa.String(length=120),
            nullable=True,
        ),
    )

    op.add_column(
        "staff_members",
        sa.Column(
            "last_name",
            sa.String(length=120),
            nullable=True,
        ),
    )

    person_rows = {
        row["id"]: row
        for row in bind.execute(
            sa.text(
                """
                SELECT id, first_name, last_name
                FROM persons
                """
            )
        ).mappings()
    }

    existing_users = list(
        bind.execute(
            sa.text(
                """
                SELECT id, person_id
                FROM user_accounts
                """
            )
        ).mappings()
    )

    existing_staff = list(
        bind.execute(
            sa.text(
                """
                SELECT id, person_id
                FROM staff_members
                """
            )
        ).mappings()
    )

    if existing_users:
        bind.execute(
            sa.text(
                """
                UPDATE user_accounts
                SET first_name = :first_name,
                    last_name = :last_name
                WHERE id = :record_id
                """
            ),
            [
                {
                    "first_name": (
                        person_rows[row["person_id"]]["first_name"] or ""
                    ),
                    "last_name": (
                        person_rows[row["person_id"]]["last_name"] or ""
                    ),
                    "record_id": row["id"],
                }
                for row in existing_users
            ],
        )

    if existing_staff:
        bind.execute(
            sa.text(
                """
                UPDATE staff_members
                SET first_name = :first_name,
                    last_name = :last_name
                WHERE id = :record_id
                """
            ),
            [
                {
                    "first_name": (
                        person_rows[row["person_id"]]["first_name"] or ""
                    ),
                    "last_name": (
                        person_rows[row["person_id"]]["last_name"] or ""
                    ),
                    "record_id": row["id"],
                }
                for row in existing_staff
            ],
        )

    # Restore the old non-null constraints.
    for table_name in (
        "user_accounts",
        "staff_members",
    ):
        op.alter_column(
            table_name,
            "first_name",
            existing_type=sa.String(length=120),
            nullable=False,
        )

        op.alter_column(
            table_name,
            "last_name",
            existing_type=sa.String(length=120),
            nullable=False,
        )

    # Remove the new staff structure.
    op.drop_constraint(
        "uq_staff_members_person_id",
        "staff_members",
        type_="unique",
    )

    op.drop_constraint(
        "fk_staff_members_person_id_persons",
        "staff_members",
        type_="foreignkey",
    )

    op.drop_column("staff_members", "leaving_date")
    op.drop_column("staff_members", "start_date")
    op.drop_column("staff_members", "employment_status")
    op.drop_column("staff_members", "person_id")

    # Remove the account-to-person structure.
    op.drop_constraint(
        "uq_user_accounts_person_id",
        "user_accounts",
        type_="unique",
    )

    op.drop_constraint(
        "fk_user_accounts_person_id_persons",
        "user_accounts",
        type_="foreignkey",
    )

    op.drop_column(
        "user_accounts",
        "person_id",
    )

    op.drop_table("persons")