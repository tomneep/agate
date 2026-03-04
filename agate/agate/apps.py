from django.apps import AppConfig
import sys


class AgateConfig(AppConfig):
    name = 'agate'

    def ready(self):
        """ Import our scheduled tasks module, which will register the tasks with the scheduler """
        # We only start the scheduler in two cases:
        # 1. We are running the development server (runserver)
        # 2. We've explicitly asked for the scheduler to be started
        if 'runserver' in sys.argv or 'runscheduler' in sys.argv:
            from .scheduled_tasks import start_scheduler
            start_scheduler()
