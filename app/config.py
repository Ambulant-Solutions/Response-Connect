import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_USER', 'response_connect')}:{os.getenv('DB_PASSWORD', 'response_connect')}"
        f"@{os.getenv('DB_HOST', 'db')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'response_connect')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CSRF will initially be applied selectively to settings writes.
    WTF_CSRF_CHECK_DEFAULT = False

    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL",
        "redis://redis:6379/0"
    )

    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://redis:6379/1"
    )

    CELERY_TASK_TRACK_STARTED = True

    CELERY_TASK_TIME_LIMIT = 30 * 60

    # Outgoing email
    MAIL_SERVER = os.getenv("MAIL_SERVER", "")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")

    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        "Response Connect <noreply@example.org>",
    )

    MAIL_TIMEOUT = int(os.getenv("MAIL_TIMEOUT", "30"))

    # Email template branding
    MAIL_BRAND_NAME = os.getenv(
        "MAIL_BRAND_NAME",
        "Response Connect",
    )

    MAIL_SUPPORT_EMAIL = os.getenv(
        "MAIL_SUPPORT_EMAIL",
        "",
    )

    MAIL_PUBLIC_URL = os.getenv(
        "MAIL_PUBLIC_URL",
        "",
    )

    PASSWORD_RESET_TOKEN_MAX_AGE = int(
        os.getenv("PASSWORD_RESET_TOKEN_MAX_AGE", "3600")
    )

    PASSWORD_RESET_SALT = os.getenv(
        "PASSWORD_RESET_SALT",
        "response-connect-password-reset",
    )
