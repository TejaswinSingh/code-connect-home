from django.utils import timezone

from home.models import Task


#_____________________________utils______________________________

def start_task(task: Task):
    task.state = task.PROCESSING
    task.full_clean()
    task.save()

def clear_task(task: Task):
    task.state = task.FINISHED
    task.exit = timezone.now()
    task.full_clean()
    task.save()