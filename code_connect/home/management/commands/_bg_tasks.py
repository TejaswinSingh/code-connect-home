

from home.models import SendEmailTask, Task

from time import sleep
from . import _utils as utils



#___________________________________________tasks________________________________________________

def empty_task(task: Task):
    utils.start_task(task)
    sleep(60 * 60)
    utils.clear_task(task)

def hello(task: Task):
    utils.start_task(task)
    print(f"hello world {task.name}")
    utils.clear_task(task)

def send_email(task: Task):
    email_task = task.sendemailtask
    utils.start_task(email_task)
    sleep(5)
    print(f"email sent to {email_task.email}")
    utils.clear_task(email_task)



#___________________________________________task table________________________________________________

TASK_TABLE = {
    0: empty_task,
    SendEmailTask.TASK_FUNCTION_ID: send_email,
    2: hello,
}