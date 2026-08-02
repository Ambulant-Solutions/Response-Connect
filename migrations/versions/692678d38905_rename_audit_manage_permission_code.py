"""Rename audit manage permission code

Revision ID: 692678d38905
Revises: fcb06a12b44b
Create Date: 2026-08-02 08:51:53.101813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '692678d38905'
down_revision = 'fcb06a12b44b'
branch_labels = None
depends_on = None


OLD_PERMISSION_CODE = "org:audit-manage"
NEW_PERMISSION_CODE = "org:audit_manage"


def upgrade() -> None:
    """
    Rename the legacy audit-management permission to the stable
    lowercase snake_case permission-code format.
    """

    op.execute(
        f"""
        UPDATE permissions
        SET name = '{NEW_PERMISSION_CODE}'
        WHERE name = '{OLD_PERMISSION_CODE}'
          AND NOT EXISTS (
              SELECT 1
              FROM permissions
              WHERE name = '{NEW_PERMISSION_CODE}'
          )
        """
    )


def downgrade() -> None:
    """
    Restore the previous permission code when downgrading.
    """

    op.execute(
        f"""
        UPDATE permissions
        SET name = '{OLD_PERMISSION_CODE}'
        WHERE name = '{NEW_PERMISSION_CODE}'
          AND NOT EXISTS (
              SELECT 1
              FROM permissions
              WHERE name = '{OLD_PERMISSION_CODE}'
          )
        """
    )