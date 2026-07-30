from functools import wraps
from urllib.parse import urlsplit

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import select
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)
from app.blueprints.auth.password_reset import (
    PasswordResetTokenError,
    validate_password_reset_token,
)
from app.blueprints.auth.services import (
    queue_password_reset_email,
)
from app.blueprints.auth.models import UserAccount  # noqa: F401
from app.extensions import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        next_url = request.form.get("next") or url_for("main.index")

        if not email:
            return render_login_page(
                email_error="Email address is required.",
                email_value=email,
                next_url=next_url,
            )

        if not password:
            return render_login_page(
                password_error="Password is required.",
                email_value=email,
                next_url=next_url,
            )

        user = db.session.scalar(select(UserAccount).where(UserAccount.email == email))
        if user is None or not check_password_hash(user.password_hash, password):
            return render_login_page(
                login_error="Invalid email or password.",
                email_value=email,
                next_url=next_url,
            )

        if not user.is_active:
            return render_login_page(
                login_error="This account is currently inactive.",
                email_value=email,
                next_url=next_url,
            )

        login_user(user, remember=request.form.get("remember") == "1")
        flash("Welcome back.", "success")
        return redirect(safe_next_url(next_url))

    return render_login_page()


@auth_bp.get("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))


def permission_required(permission_name: str):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please sign in to continue.", "info")
                return redirect(url_for("auth.login"))

            if not current_user.has_permission(permission_name):
                flash("You do not have permission to access this section.", "danger")
                return redirect(url_for("main.index"))

            return view_func(*args, **kwargs)

        return wrapped

    return decorator

def any_permission_required(
    *permission_names: str,
):
    if not permission_names:
        raise ValueError(
            "At least one permission name is required."
        )

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped(*args, **kwargs):
            if not any(
                current_user.has_permission(name)
                for name in permission_names
            ):
                flash(
                    "You do not have permission to access "
                    "this section.",
                    "danger",
                )
                return redirect(
                    url_for("main.index")
                )

            return view_func(*args, **kwargs)

        return wrapped

    return decorator


@auth_bp.get("/permissions")
@permission_required("auth:manage_users")
def permissions():
    return render_template("permissions.html")


@auth_bp.route(
    "/lost-password",
    methods=["GET", "POST"],
)
@auth_bp.route(
    "/forgot-password",
    methods=["GET", "POST"],
)
def lost_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = (
            request.form.get("email") or ""
        ).strip().lower()

        if not email:
            return render_lost_password_page(
                email_error="Email address is required.",
                email_value=email,
            )

        user = db.session.scalar(
            select(UserAccount).where(
                UserAccount.email == email
            )
        )

        if user is not None and user.is_active:
            try:
                queue_password_reset_email(user)
            except Exception:
                current_app.logger.exception(
                    "Could not queue password-reset email "
                    "for user %s.",
                    user.id,
                )

        flash(
            "If an active account exists for that email address, "
            "password reset instructions will be sent.",
            "info",
        )

        return redirect(
            url_for("auth.lost_password")
        )

    return render_lost_password_page()

@auth_bp.route(
    "/reset-password/<token>",
    methods=["GET", "POST"],
)
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    try:
        token_result = validate_password_reset_token(token)
    except PasswordResetTokenError as exc:
        return render_reset_password_page(
            token_valid=False,
            token_error=str(exc),
        )

    if request.method == "POST":
        password = request.form.get("password") or ""
        password_confirmation = (
            request.form.get("password_confirmation") or ""
        )

        password_error = validate_new_password(
            password=password,
            confirmation=password_confirmation,
            user=token_result.user,
        )

        if password_error:
            return render_reset_password_page(
                token_valid=True,
                token=token,
                password_error=password_error,
            )

        token_result.user.password_hash = (
            generate_password_hash(password)
        )

        db.session.commit()

        flash(
            "Your password has been reset. You can now sign in.",
            "success",
        )

        return redirect(url_for("auth.login"))

    return render_reset_password_page(
        token_valid=True,
        token=token,
    )


def render_login_page(**context):
    default_context = {
        "installation_name": "Example Ambulance Service",
        "login_url": url_for("auth.login"),
        "forgot_password_url": url_for("auth.lost_password"),
    }
    default_context.update(context)
    return render_template("auth/login.html", **default_context)


def render_lost_password_page(**context):
    default_context = {
        "installation_name": "Example Ambulance Service",
        "lost_password_url": url_for(
            "auth.lost_password"
        ),
        "login_url": url_for("auth.login"),
    }

    default_context.update(context)

    return render_template(
        "auth/lost_password.html",
        **default_context,
    )


def safe_next_url(next_url: str | None) -> str:
    if not next_url:
        return url_for("main.index")

    parsed = urlsplit(next_url)
    if parsed.scheme or parsed.netloc:
        return url_for("main.index")

    return next_url

def validate_new_password(
    *,
    password: str,
    confirmation: str,
    user: UserAccount,
) -> str | None:
    """Validate a password selected during account recovery."""

    if not password:
        return "A new password is required."

    if len(password) < 12:
        return (
            "Your password must contain at least 12 characters."
        )

    if len(password) > 128:
        return (
            "Your password must not exceed 128 characters."
        )

    if password != confirmation:
        return "The password confirmation does not match."

    if check_password_hash(
        user.password_hash,
        password,
    ):
        return (
            "Your new password must be different from your "
            "current password."
        )

    return None


def render_reset_password_page(**context):
    default_context = {
        "installation_name": "Example Ambulance Service",
        "login_url": url_for("auth.login"),
    }

    default_context.update(context)

    return render_template(
        "auth/reset_password.html",
        **default_context,
    )
