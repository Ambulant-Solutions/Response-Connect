from __future__ import annotations

import re
import uuid
from collections import OrderedDict

from flask import (
    abort,
    flash,
    redirect,
    render_template,
    url_for,
)
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.blueprints.auth import permission_required
from app.blueprints.auth.catalogue import (
    PERMISSION_CATEGORY_LABELS,
    ensure_permission_catalogue,
)
from app.blueprints.auth.models import (
    Permission,
    Role,
    UserAccount,
)
from app.blueprints.org.settings import settings_bp
from app.blueprints.org.settings.forms import (
    RoleActionForm,
    RoleForm,
)
from app.extensions import db


ROLE_CODE_PATTERN = re.compile(
    r"^[a-z][a-z0-9_]*$"
)


def normalise_role_code(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def load_permissions() -> list[Permission]:
    statement = select(Permission).order_by(
        Permission.category,
        Permission.name,
    )

    return list(db.session.scalars(statement).all())


def load_roles() -> list[Role]:
    statement = (
        select(Role)
        .options(
            selectinload(Role.permissions),
            selectinload(Role.users),
        )
        .order_by(
            Role.sort_order,
            Role.display_name,
            Role.name,
        )
    )

    return list(
        db.session.scalars(statement).unique().all()
    )


def get_role_or_404(
    role_id: uuid.UUID,
) -> Role:
    statement = (
        select(Role)
        .where(Role.id == role_id)
        .options(
            selectinload(Role.permissions),
            selectinload(Role.users),
        )
    )

    role = db.session.scalar(statement)

    if role is None:
        abort(404)

    return role


def group_permissions(
    permissions: list[Permission],
) -> list[dict]:
    grouped: OrderedDict[str, list[Permission]] = (
        OrderedDict()
    )

    for permission in permissions:
        grouped.setdefault(
            permission.category,
            [],
        ).append(permission)

    return [
        {
            "code": category,
            "label": PERMISSION_CATEGORY_LABELS.get(
                category,
                category.replace("_", " ").title(),
            ),
            "permissions": category_permissions,
        }
        for category, category_permissions
        in grouped.items()
    ]


def configure_role_form(
    form: RoleForm,
    permissions: list[Permission],
) -> None:
    form.permission_ids.choices = [
        (
            str(permission.id),
            permission.description,
        )
        for permission in permissions
    ]


def validate_role_form(
    form: RoleForm,
    *,
    permissions: list[Permission],
    current_role: Role | None,
) -> tuple[bool, list[Permission]]:
    valid = True
    code = normalise_role_code(form.name.data)

    if not ROLE_CODE_PATTERN.fullmatch(code):
        form.name.errors.append(
            "Use lowercase letters, numbers and "
            "underscores only. The code must begin "
            "with a letter."
        )
        valid = False

    duplicate_code = select(Role.id).where(
        func.lower(Role.name) == code.lower()
    )

    if current_role is not None:
        duplicate_code = duplicate_code.where(
            Role.id != current_role.id
        )

    if db.session.scalar(duplicate_code) is not None:
        form.name.errors.append(
            "This role code is already in use."
        )
        valid = False

    permission_by_id = {
        str(permission.id): permission
        for permission in permissions
    }

    selected_permissions: list[Permission] = []

    for permission_id in (
        form.permission_ids.data or []
    ):
        permission = permission_by_id.get(
            permission_id
        )

        if permission is None:
            form.permission_ids.errors.append(
                "One or more selected permissions "
                "are invalid."
            )
            valid = False
            continue

        selected_permissions.append(permission)

    if current_role is not None:
        if (
            current_role.is_system
            and code != current_role.name
        ):
            form.name.errors.append(
                "The code of a system role cannot "
                "be changed."
            )
            valid = False

        if current_role.name == "admin":
            # Ignore submitted permission values and
            # preserve all permissions.
            selected_permissions = permissions

    return valid, selected_permissions


def apply_role_form(
    role: Role,
    *,
    form: RoleForm,
    permissions: list[Permission],
) -> None:
    if not role.is_system:
        role.name = normalise_role_code(
            form.name.data
        )

    role.display_name = (
        form.display_name.data.strip()
    )

    role.description = (
        form.description.data.strip()
    )

    role.sort_order = form.sort_order.data

    if role.name == "admin":
        role.permissions = permissions
        role.is_active = True
    else:
        role.permissions = permissions


@settings_bp.get("/roles")
@permission_required("auth:manage_users")
def role_index():
    ensure_permission_catalogue()

    return render_template(
        "org/settings/roles/index.html",
        roles=load_roles(),
        action_form=RoleActionForm(),
        active_org_section="settings",
    )


@settings_bp.route(
    "/roles/new",
    methods=["GET", "POST"],
)
@permission_required("auth:manage_users")
def role_create():
    ensure_permission_catalogue()

    permissions = load_permissions()
    form = RoleForm()

    configure_role_form(form, permissions)

    if not form.is_submitted():
        form.sort_order.data = 100

    base_valid = form.validate_on_submit()
    references_valid = False
    selected_permissions = []

    if form.is_submitted():
        (
            references_valid,
            selected_permissions,
        ) = validate_role_form(
            form,
            permissions=permissions,
            current_role=None,
        )

    if base_valid and references_valid:
        role = Role(
            name=normalise_role_code(
                form.name.data
            ),
            display_name=(
                form.display_name.data.strip()
            ),
            description=(
                form.description.data.strip()
            ),
            is_system=False,
            is_active=True,
            sort_order=form.sort_order.data,
            permissions=selected_permissions,
        )

        db.session.add(role)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The role could not be created. "
                "Check that its code is unique.",
                "danger",
            )
        else:
            flash(
                "Role created successfully.",
                "success",
            )

            return redirect(
                url_for("org.settings.role_index")
            )

    return render_template(
        "org/settings/roles/form.html",
        form=form,
        role=None,
        permission_groups=group_permissions(
            permissions
        ),
        code_locked=False,
        permissions_locked=False,
        active_org_section="settings",
    )


@settings_bp.route(
    "/roles/<uuid:role_id>/edit",
    methods=["GET", "POST"],
)
@permission_required("auth:manage_users")
def role_edit(role_id: uuid.UUID):
    ensure_permission_catalogue()

    role = get_role_or_404(role_id)
    permissions = load_permissions()
    form = RoleForm()

    configure_role_form(form, permissions)

    if not form.is_submitted():
        form.name.data = role.name
        form.display_name.data = role.label
        form.description.data = role.description
        form.permission_ids.data = [
            str(permission.id)
            for permission in role.permissions
        ]
        form.sort_order.data = role.sort_order

    base_valid = form.validate_on_submit()
    references_valid = False
    selected_permissions = []

    if form.is_submitted():
        (
            references_valid,
            selected_permissions,
        ) = validate_role_form(
            form,
            permissions=permissions,
            current_role=role,
        )

    if base_valid and references_valid:
        apply_role_form(
            role,
            form=form,
            permissions=selected_permissions,
        )

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

            flash(
                "The role could not be saved.",
                "danger",
            )
        else:
            flash(
                "Role updated successfully.",
                "success",
            )

            return redirect(
                url_for("org.settings.role_index")
            )

    return render_template(
        "org/settings/roles/form.html",
        form=form,
        role=role,
        permission_groups=group_permissions(
            permissions
        ),
        code_locked=role.is_system,
        permissions_locked=(
            role.name == "admin"
        ),
        active_org_section="settings",
    )


@settings_bp.post(
    "/roles/<uuid:role_id>/deactivate"
)
@permission_required("auth:manage_users")
def role_deactivate(role_id: uuid.UUID):
    form = RoleActionForm()

    if not form.validate_on_submit():
        abort(400)

    role = get_role_or_404(role_id)

    if role.is_system:
        flash(
            "System roles cannot be deactivated.",
            "danger",
        )
    elif any(
        user.is_active
        for user in role.users
    ):
        flash(
            "Remove this role from its active users "
            "before deactivating it.",
            "danger",
        )
    else:
        role.is_active = False
        db.session.commit()

        flash("Role deactivated.", "success")

    return redirect(
        url_for("org.settings.role_index")
    )


@settings_bp.post(
    "/roles/<uuid:role_id>/activate"
)
@permission_required("auth:manage_users")
def role_activate(role_id: uuid.UUID):
    form = RoleActionForm()

    if not form.validate_on_submit():
        abort(400)

    role = get_role_or_404(role_id)
    role.is_active = True
    db.session.commit()

    flash("Role activated.", "success")

    return redirect(
        url_for("org.settings.role_index")
    )


@settings_bp.get("/permissions")
@permission_required("auth:manage_users")
def permission_index():
    ensure_permission_catalogue()

    permissions = load_permissions()

    role_counts = dict(
        db.session.execute(
            select(
                Permission.id,
                func.count(Role.id),
            )
            .outerjoin(Permission.roles)
            .group_by(Permission.id)
        ).all()
    )

    return render_template(
        "org/settings/permissions/index.html",
        permission_groups=group_permissions(
            permissions
        ),
        role_counts=role_counts,
        active_org_section="settings",
    )