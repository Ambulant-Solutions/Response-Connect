from celery import Celery

from app import create_app


def make_celery(app=None):
    app = app or create_app()

    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
        include=[
            "app.tasks.test",
            "app.blueprints.jobs.tasks",
        ],
    )

    celery.conf.update(app.config)

    class FlaskContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskContextTask

    return celery


celery = make_celery()