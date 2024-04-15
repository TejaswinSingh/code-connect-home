from django.db import models


#___________________________________________base model________________________________________________

class Task(models.Model):

    #_____________________________choices______________________________

    QUEUED = 'Q'
    PROCESSING = 'P'
    FINISHED = 'F'

    STATE_CHOICES = {
        QUEUED: 'QUEUED',
        PROCESSING: 'PROCESSING',
        FINISHED: 'FINISHED'
    }

    #_____________________________fields______________________________

    name = models.CharField(max_length=255)
    arrival = models.DateTimeField(auto_now_add=True)
    exit = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=QUEUED)
    task_function_id = models.PositiveSmallIntegerField(default=0)

    # NOTE: child class must have these fields
    # result = models.CharField(max_length=255)
    # TASK_FUNCTION_ID = 36

    def __str__(self):
        return f"Task: {self.name} [State: {self.STATE_CHOICES[self.state]}]"



#___________________________________________derived models________________________________________________

class SendEmailTask(Task):
    email = models.EmailField(max_length=100)
    result = None
    TASK_FUNCTION_ID = 1

    def save(self, *args, **kwargs):
        self.task_function_id = self.TASK_FUNCTION_ID
        # call the real save() method
        super(SendEmailTask, self).save(*args, **kwargs)

    def __str__(self):
        return f"Task: Send mail to {self.email} [State: {self.STATE_CHOICES[self.state]}]"