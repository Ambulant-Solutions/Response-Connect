from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv

from app import create_app
from app.extensions import db

load_dotenv()

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

app = create_app()
config.set_main_option("sqlalchemy.url", app.config["SQLALCHEMY_DATABASE_URI"])

target_metadata = db.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with app.app_context():
        connectable = db.engine
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
