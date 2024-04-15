from django.core.management.base import BaseCommand, CommandError

from home.models import Task

from . import _bg_tasks
from . import _utils as utils
from time import sleep
import sys, os



#___________________________________________commands________________________________________________

class Command(BaseCommand):
    help = "starts executing any queued tasks"

    def handle(self, *args, **options):
        while True:
            try:
                task = Task.objects.order_by('arrival').filter(state=Task.QUEUED).first()
                if task:
                    _bg_tasks.TASK_TABLE[task.task_function_id](task)
                else:
                    sleep(1)
            except Exception as e:
                if task:
                    utils.clear_task(task)
                self.stderr.write(
                    self.style.ERROR(f'{e}')
                )
            except KeyboardInterrupt:
                self.stderr.write(
                    self.style.ERROR(f'Keyboard Interrupt- stoped running tasks')
                )
                try:
                    sys.exit(130)
                except SystemExit:
                        os._exit(130)

            