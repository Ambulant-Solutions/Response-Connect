from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select

from app.blueprints.auth.models import (
    Permission,
    Role,
)
from app.extensions import db


PERMISSION_DEFINITIONS = (
    {
        "name": "auth:manage_users",
        "description": (
            "Manage users, roles and access control"
        ),
        "category": "auth",
    },
    {
        "name": "personal:read",
        "description": "Access personal workspace",
        "category": "personal",
    },
    {
        "name": "org:read",
        "description": "Access organisation workspace",
        "category": "org",
    },
    {
        "name": "org:manage",
        "description": (
            "Manage operational organisation settings"
        ),
        "category": "org",
    },
    {
        "name": "org:audit-manage",
        "description": "Manage Audit workspace",
        "category": "org",
    },
    {
        "name": "api:read",
        "description": "Read API resources",
        "category": "api",
    },
    {
        "name": "api:write",
        "description": "Write API resources",
        "category": "api",
    },
    {
        "name": "recruitment:manage",
        "description": (
            "Manage job applications and recruitment"
        ),
        "category": "recruitment",
    },
    {
        "name": "hr:read",
        "description": (
            "View staff records and HR compliance information"
        ),
        "category": "hr",
    },
    {
        "name": "hr:manage",
        "description": (
            "Manage staff records, positions and clinical grades"
        ),
        "category": "hr",   
    },
    {
        "name": "hr:manage_training",
        "description": (
            "Manage mandatory training courses and requirements"
        ),
        "category": "hr",
    },
    {
        "name": "hr:verify_training",
        "description": (
            "Verify or reject staff training certificates"
        ),
        "category": "hr",
    },
    {
        "name": "personal:upload_training",
        "description": (
            "Upload training certificates to the current staff record"
        ),
        "category": "personal",
    },
    {
        "name": "external:manage",
        "description": (
            "Manage external forms and complaints"
        ),
        "category": "external",
    },
)


PERMISSION_CATEGORY_LABELS = {
    "auth": "Access control",
    "personal": "Personal workspace",
    "org": "Organisation administration",
    "api": "API access",
    "recruitment": "Recruitment",
    "hr": "Human resources",
    "external": "External services",
}


DEFAULT_STAFF_PERMISSIONS = {
    "personal:read",
    "personal:upload_training",
    "org:read",
}


@dataclass(frozen=True)
class PermissionSeedResult:
    permissions_created: int
    roles_created: int

    @property
    def changed(self) -> bool:
        return (
            self.permissions_created > 0
            or self.roles_created > 0
        )


def ensure_permission_catalogue(
) -> PermissionSeedResult:
    permissions_created = 0
    roles_created = 0

    existing_permissions = {
        permission.name: permission
        for permission in db.session.scalars(
            select(Permission)
        ).all()
    }

    for definition in PERMISSION_DEFINITIONS:
        permission = existing_permissions.get(
            definition["name"]
        )

        if permission is None:
            permission = Permission(
                name=definition["name"],
                description=definition["description"],
                category=definition["category"],
            )

            db.session.add(permission)
            existing_permissions[
                definition["name"]
            ] = permission

            permissions_created += 1
        else:
            permission.description = (
                definition["description"]
            )
            permission.category = (
                definition["category"]
            )

    db.session.flush()

    admin_role = db.session.scalar(
        select(Role).where(Role.name == "admin")
    )

    if admin_role is None:
        admin_role = Role(
            name="admin",
            display_name="Administrator",
            description=(
                "System-wide administrative role"
            ),
            is_system=True,
            is_active=True,
            sort_order=10,
        )

        db.session.add(admin_role)
        roles_created += 1

    admin_role.display_name = "Administrator"
    admin_role.description = (
        "System-wide administrative role"
    )
    admin_role.is_system = True
    admin_role.is_active = True
    admin_role.sort_order = 10

    # Administrator always receives every permission.
    admin_role.permissions = list(
        existing_permissions.values()
    )

    staff_role = db.session.scalar(
        select(Role).where(Role.name == "staff")
    )

    if staff_role is None:
        staff_role = Role(
            name="staff",
            display_name="Staff",
            description="Standard staff access role",
            is_system=True,
            is_active=True,
            sort_order=20,
        )

        db.session.add(staff_role)
        roles_created += 1
    else:
        staff_role.display_name = (
            staff_role.display_name or "Staff"
        )
        staff_role.is_system = True
        staff_role.is_active = True

    # Add any missing mandatory permissions without removing
    # additional permissions that administrators have assigned.
    for permission_name in DEFAULT_STAFF_PERMISSIONS:
        permission = existing_permissions.get(permission_name)

        if (
            permission is not None
            and permission not in staff_role.permissions
        ):
            staff_role.permissions.append(permission)

    db.session.commit()

    return PermissionSeedResult(
        permissions_created=permissions_created,
        roles_created=roles_created,
    )