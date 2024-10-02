from django_scheduled_tasks.register import register_task


@register_task(interval=0.5)
def test_task():
    raise Exception("task")
