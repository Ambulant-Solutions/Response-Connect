import uuid

import click
from flask import Flask
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app.blueprints.api import api_bp
from app.blueprints.auth import auth_bp
from app.blueprints.auth.models import Permission, Role, UserAccount
from app.blueprints.external import external_bp
from app.blueprints.job_application import job_application_bp
from app.blueprints.main import main_bp
from app.blueprints.org import org_bp
from app.blueprints.personal import personal_bp
from app.config import Config
from app.extensions import db, login_manager, migrate


HARDWIRED_PERMISSIONS = (
    ("auth:manage_users", "Manage users and access control", "auth"),
    ("personal:read", "Access personal workspace", "personal"),
    ("org:read", "Access organisation workspace", "org"),
    ("org:manage", "Manage operational organisation settings", "org"),
    ("api:read", "Read API resources", "api"),
    ("api:write", "Write API resources", "api"),
    ("recruitment:manage", "Manage job applications and recruitment", "recruitment"),
    ("external:manage", "Manage external forms and complaints", "external"),
)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to continue."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return db.session.get(UserAccount, uuid.UUID(str(user_id)))
        except (TypeError, ValueError):
            return None

    @app.cli.command("create-admin")
    @click.option("--email", required=True, prompt=True, help="Primary email address for the initial administrator account.")
    @click.option("--password", required=True, prompt=True, hide_input=True, confirmation_prompt=True, help="Initial password for the administrator account.")
    @click.option("--first-name", default="System", show_default=True, help="Administrator first name.")
    @click.option("--last-name", default="Administrator", show_default=True, help="Administrator last name.")
    def create_admin_command(email: str, password: str, first_name: str, last_name: str) -> None:
        with app.app_context():
            seed_permission_system()
            user = db.session.scalar(select(UserAccount).where(UserAccount.email == email.strip().lower()))
            if user is None:
                user = UserAccount(
                    email=email.strip().lower(),
                    first_name=(first_name or "").strip(),
                    last_name=(last_name or "").strip(),
                    password_hash=generate_password_hash(password),
                    is_active=True,
                )
                db.session.add(user)
            else:
                user.first_name = (first_name or "").strip()
                user.last_name = (last_name or "").strip()
                user.password_hash = generate_password_hash(password)
                user.is_active = True

            admin_role = db.session.scalar(select(Role).where(Role.name == "admin"))
            if admin_role is not None and admin_role not in user.roles:
                user.roles.append(admin_role)

            db.session.commit()
            click.echo(f"Admin account ready: {user.email}")

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(personal_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(job_application_bp)
    app.register_blueprint(external_bp)

    return app


def seed_permission_system() -> None:
    permission_records = {}
    for permission_name, description, category in HARDWIRED_PERMISSIONS:
        permission = db.session.scalar(select(Permission).where(Permission.name == permission_name))
        if permission is None:
            permission = Permission(name=permission_name, description=description, category=category)
            db.session.add(permission)
        else:
            permission.description = description
            permission.category = category
        permission_records[permission_name] = permission

    admin_role = db.session.scalar(select(Role).where(Role.name == "admin"))
    if admin_role is None:
        admin_role = Role(name="admin", description="System-wide administrative role")
        db.session.add(admin_role)

    standard_role = db.session.scalar(select(Role).where(Role.name == "staff"))
    if standard_role is None:
        standard_role = Role(name="staff", description="Standard staff access role")
        db.session.add(standard_role)

    admin_role.permissions = []
    for permission in permission_records.values():
        if permission not in admin_role.permissions:
            admin_role.permissions.append(permission)

    standard_role.permissions = []
    for permission_name in (
        "personal:read",
        "org:read",
    ):
        if permission_name in permission_records and permission_records[permission_name] not in standard_role.permissions:
            standard_role.permissions.append(permission_records[permission_name])

    db.session.commit()
