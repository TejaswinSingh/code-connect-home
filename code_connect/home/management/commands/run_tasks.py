#_____________________________________________________________________________________________________
""" 
    - defines the `manage.py run_tasks` command
"""

__author__ = "Tejaswin Singh, "
__copyright__ = "Copyright 2024, Code Connect Home"
__credits__ = ["Tejaswin Singh", "", ]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Tejaswin Singh"
__email__ = "tejaswin.cs08@gmail.com"
__status__ = "Development"

#_____________________________________________________________________________________________________


from django.core.management.base import BaseCommand, CommandError

from home.models import Task

from time import sleep
import sys, os
from ._bg_tasks import execute_task



#___________________________________________commands________________________________________________

class Command(BaseCommand):
    """ run_tasks command. Used for running background tasks. """

    help = "starts executing any queued tasks"

    def handle(self, *args, **options):

        while True:
            try:
                # fetch a queued task from db
                task = Task.objects.order_by('arrival').filter(state=Task.QUEUED).first()
                if task:
                    # call `execute_task` function which looks up TASK_TABLE and 
                    # calls the appropiate function for the passed task
                    execute_task(self, task)
                else:
                    # don't hammer the db continously
                    sleep(1)
            except Exception as e:
                if task:
                    task.abort_task()
                # red-colored output
                self.stderr.write(
                    self.style.ERROR(f'Task failed-\t{e}')
                )
            except KeyboardInterrupt:
                self.stderr.write(
                    self.style.ERROR(f'Keyboard Interrupt\t--stoped running tasks')
                )
                try:
                    sys.exit(130)
                except SystemExit:
                        os._exit(130)