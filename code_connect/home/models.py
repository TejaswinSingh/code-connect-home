#_____________________________________________________________________________________________________
""" 
    - defines models used by the `home` app.
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


from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

#___________________________________________base model________________________________________________

class Task(models.Model):
    """
        - base Task model. All the other Task models are derived from it.
        AbstractModel was not used since it can't be viewed in the admin-site.
    """

    #_____________________________choices______________________________

    QUEUED = 'Q'
    PROCESSING = 'P'
    FINISHED = 'F'
    ABORTED = 'A'

    STATE_CHOICES = {
        QUEUED: 'QUEUED',
        PROCESSING: 'PROCESSING',
        FINISHED: 'FINISHED',
        ABORTED: 'ABORTED'
    }

    #_____________________________fields________________________________

    name = models.CharField(max_length=255)
    arrival = models.DateTimeField(auto_now_add=True)
    exit = models.DateTimeField(blank=True, null=True)
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default=QUEUED)
    task_function_id = models.PositiveSmallIntegerField(default=0)  # function id in TASK_TABLE

    # NOTE: child class must have their own definitions of the fields below
    # result = models.CharField(max_length=255)

    #_____________________________instance methods______________________
    
    def start_task(self):
        """ call before performing the task """

        self.state = Task.PROCESSING
        self.full_clean()
        self.save()

    def clear_task(self):
        """ call after the task is performed """

        self.state = Task.FINISHED
        self.exit = timezone.now()
        self.full_clean()
        self.save()

    def abort_task(self):
        """ call if there was some error while performing the task """

        self.state = Task.ABORTED
        self.full_clean()
        self.save()

    def __str__(self) -> str:
        return f"Task: {self.name} [State: {self.STATE_CHOICES[self.state]}]"



#___________________________________________derived models____________________________________________

class SendInviteTask(Task):
    """
        - task reponsible for sending invite mails to Invitation objects.
        Call send function to send the mail.
    """

    #_________________________________fields___________________________________

    invite = models.ForeignKey(
        "members.Invitation",
        on_delete=models.SET_NULL,
        null=True
    )
    result = None
    TASK_FUNCTION_ID = 1

    #_____________________________instance methods______________________________

    def save(self, *args, **kwargs):
        """ Custom save. Sets {task_function_id} """
        self.task_function_id = self.TASK_FUNCTION_ID
        # call the real save() method
        super(SendInviteTask, self).save(*args, **kwargs)

    def send(self) -> None:
        """ Sends the invitation email for the referenced {invite} """

        if not self.invite:
            raise ValueError("Invite is set to null.")
        
        invite = self.invite
        email = invite.mail_address
        home_link = f'http://192.168.230.155:2004'
        link = f'http://192.168.230.155:2004/members/registration/?i={invite.code}'
        contact = "codeconnectcuj@mail.edu"

        # send customized html email
        html_message = render_to_string('home/invitation_mail.html', context={'link': link, 'home_link': home_link, 'email': email, 'contact': contact})
        send_mail(
            subject = f"Mail from Code Connect!",
            message = strip_tags(html_message),
            from_email = settings.EMAIL_HOST_USER,
            recipient_list = [f'{email}'],
            fail_silently = False,
            html_message=html_message
        )

        # now update the invite object
        invite.sent_at = timezone.now()
        invite.full_clean()
        invite.save()

    def __str__(self) -> None:
        if self.invite:
            return f"Task: Send mail to {self.invite.mail_address} [State: {self.STATE_CHOICES[self.state]}]"
        else:
            return super(SendInviteTask, self).__str__()