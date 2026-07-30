from app.celery import celery


@celery.task
def test_task():
    return "Celery is working"