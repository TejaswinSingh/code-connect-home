#_____________________________________________________________________________________________________
""" 
    - defines tests for `home.models`.
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

from django.test import TestCase

from home.models import Task, SendInviteTask
from members.models import Invitation

class TaskModelTests(TestCase):
    """ tests for Task """

    #_______________________utilities_________________________

    def create_simple_task(
        self,
        name="Example Task"
    ):
        fields = {
            'name': name,
        }
        t = Task(**(fields))
        t.full_clean()
        t.save()
        return t     

    #_______________________tests______________________________

    def test_defaults(self):
        """
            - tests the default values of {state}, {task_function_id},
            {arrival} and {exit}
        """
        t = self.create_simple_task()
        self.assertEqual(t.state, t.QUEUED)
        self.assertEqual(t.task_function_id, 0)
        self.assertEqual(t.exit, None)
        self.assertNotEqual(t.arrival, None)

    def test_instance_methods(self):
        """
            - tests the start_task(), clear_task() and abort_task()
            methods
        """
        t = self.create_simple_task()
        self.assertEqual(t.state, t.QUEUED)

        t.start_task()
        self.assertEqual(t.state, t.PROCESSING)

        self.assertEqual(t.exit, None)
        t.clear_task()
        self.assertEqual(t.state, t.FINISHED)
        self.assertNotEqual(t.arrival, None)

        t.abort_task()
        self.assertEqual(t.state, t.ABORTED)


class SendInviteTaskModelTests(TestCase):
    """ tests for SendInviteTask """

    #_______________________utilities_________________________

    def create_simple_send_invite_task(
        self,
        name="Example Task", invite=None
    ):
        fields = {
            'name': name,
            'invite': invite
        }
        t = SendInviteTask(**(fields))
        t.full_clean()
        t.save()
        return t
    
    def create_simple_invitation(
        self,
        mail_address="johniver10@mail.dev", sent_at=None, 
        accepted=False
    ):
        fields = {
            'mail_address': mail_address,
            'sent_at': sent_at,
            'accepted': accepted,
        }
        i = Invitation(**(fields))
        i.full_clean()
        i.save()
        return i

    #_______________________tests_____________________________

    def test_task_function_id(self):
        """
            - tests the default values of {task_function_id},
            is correct.
        """
        i = self.create_simple_invitation()
        t = self.create_simple_send_invite_task(invite=i)
        self.assertEqual(t.task_function_id, SendInviteTask.TASK_FUNCTION_ID)

    def test_null_invite(self):
        """
            - tests that a ValueError is raised if we call send() on a task
            whose referenced invite was deleted
        """
        i = self.create_simple_invitation()
        t = self.create_simple_send_invite_task(invite=i)
        # now delete the invite referenced by our task
        i.delete()
        # refetch task from db
        t = SendInviteTask.objects.get(pk=t.pk)
        with self.assertRaisesMessage(ValueError, "Invite is set to null."):
            t.send()

    def test_invite_updated(self):
        """
            - tests that the invite's {sent_at} field was
            updated after calling send()
        """
        i = self.create_simple_invitation()
        t = self.create_simple_send_invite_task(invite=i)
        self.assertEqual(i.sent_at, None)
        t.send()
        self.assertNotEqual(i.sent_at, None)