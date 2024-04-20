#_____________________________________________________________________________________________________
""" 
    - defines the functions that are called when Tasks 
    objects are executed.
"""

__author__ = "Tejaswin Singh, "
__copyright__ = "Copyright 2024, Code Connect Home"
__credits__ = ["Tejaswin Singh", "", ]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Tejaswin Singh"
__email__ = "tejaswin.cs08@gmail.com"
__status__ = "Development"

#______________________________________________imports_________________________________________________


from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError

from home.models import SendInviteTask, Task

from smtplib import SMTPException


#___________________________________________utilities________________________________________________

def execute_task(cmd: BaseCommand, task: Task) -> None:
    """ 
        - looks up TASK_TABLE and calls the appropiate function for the passed task
    """
    TASK_TABLE[task.task_function_id](cmd, task)

#___________________________________________tasks________________________________________________

def hello(cmd: BaseCommand, task: Task) -> None:
    """ function called by default {task_function_id} """

    task.start_task()
    # green colored output
    cmd.stderr.write(
        cmd.style.SUCCESS(f'hello world {task.name}')
    )
    task.clear_task()


def send_invite(cmd: BaseCommand, task: Task) -> None:
    """ called by SendInviteTask """

    invite_task = task.sendinvitetask     # extract SendInviteTask from Task
    invite_task.start_task()

    try:
        invite_task.send()
        cmd.stderr.write(
            cmd.style.SUCCESS(f'invite sent to {invite_task.invite.mail_address}')
        )
        invite_task.clear_task()
    except (SMTPException, ValueError, ValidationError) as e:
        invite_task.abort_task()
        # log the error
        cmd.stderr.write(
            cmd.style.ERROR(f'Task aborted- {str(invite_task)} [{e}]')
        )
    


#___________________________________________task table________________________________________________

#
#   * this table is used to map functions to a function_id.
#   * Like `hello` is mapped to id 0.
#   * Each Task object has a {task_function_id}. So when a task is to be
#   * executed, we will call the function mapped to its {task_function_id}.
#

TASK_TABLE = {
    0: hello,
    SendInviteTask.TASK_FUNCTION_ID: send_invite,   # 1
}