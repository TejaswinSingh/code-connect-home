from django.test import TestCase, SimpleTestCase
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone

from datetime import timedelta

from members import utils
from members.models import Member, CustomUser, Invitation



class MemberModelTests(TestCase):
    """ Tests for Member """

    #_______________________utilities_________________________

    def create_simple_member(
        self,
        firstname="John", lastname="Oliver", email="johniver10@mail.dev", 
        roll="22becse44", contact="+91 9999999999", programme='CSE', semester='4',
        has_graduated=False
    ):
        fields = {
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'roll': roll,
            'contact': contact,
            'programme': programme,
            'semester': semester,
            'has_graduated': has_graduated
        }
        return Member(**(fields))

    # TODO: learn more about usage of the method below
    @classmethod
    def setUpTestData(cls):
        pass


    #_______________________tests_________________________

    def test_roll_format(self):
        """
            - tests that roll matches the roll-format of the selected programme
        """
        m = self.create_simple_member(roll='22beece23', programme='AVI')
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_has_graduated(self):
        """
            - tests that only a Member in the 8th Sem can have {has_graduated} set to True
        """
        with self.assertRaises(ValidationError):
            m = self.create_simple_member(has_graduated=True, semester='4')
            m.full_clean()

        # no error will be raised in this case
        m = self.create_simple_member(has_graduated=True, semester='8')
        m.full_clean()

    def test_user_is_created(self):
        """
            - tests that a CustomUser object is created for each Member object
        """
        m = self.create_simple_member()
        m.full_clean()
        m.save()
        self.assertIsInstance(m.user, CustomUser)

    def test_default_profile_pic(self):
        """
            - tests that if {profile_pic} is not provided, then a default one is used
        """
        m = self.create_simple_member()
        self.assertEqual(m.profile_pic, 'defaults/profile.png')


class InvitationModelTests(TestCase):
    """ Tests for Invitation """

    #_______________________utilities_________________________

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
        return Invitation(**(fields))
    

    #_______________________tests_________________________
    
    def test_code_format(self):
        """
            - tests that {code} generated starts with 'CUJ'
        """
        i = self.create_simple_invitation()
        i.full_clean()
        self.assertTrue(i.code.startswith('CUJ'))

    def test_unique_code(self):
        """
            - tests that a unique {code} is generated for each Invitation object
        """
        i = self.create_simple_invitation(mail_address="unique@mail.com")
        i.full_clean()
        i.save()

        # if code is not unique then MultipleObjectsReturned error could have been generated
        Invitation.objects.get(code=i.code) 
    
    def test_has_expired(self):
        """
            - tests `has_expired()` instance method
        """
        # create an expired invitation
        i = self.create_simple_invitation(sent_at=utils.get_expired_invitation_time())
        i2 = self.create_simple_invitation( 
            mail_address="example@mail.com", 
            sent_at=timezone.now() - timedelta(hours=4) # valid invitation
        )
        i.full_clean()
        i.save()
        i2.full_clean()
        i2.save()
        self.assertEqual(i.has_expired(), True)
        self.assertEqual(i2.has_expired(), False)

    def test_clean_db(self):
        """
            - tests `clean_db()` class method to see if it deletes all expired and 
            unaccepted invites
        """
        i = self.create_simple_invitation(
            mail_address="expired@mail.edu",
            sent_at=utils.get_expired_invitation_time()
        )
        i.full_clean()
        i.save()
        Invitation.clean_db()
        with self.assertRaises(ObjectDoesNotExist):
            Invitation.objects.get(id=i.pk) # i doesn't exist thus it was deleted

    def test_accepted_invite(self):
        """
            - tests that a new Invitation object won't be created
            if an accepted Invitation for the same mail already exists
        """
        i = self.create_simple_invitation(mail_address="accepted@mail.com", accepted=True)
        i.full_clean()
        i.save()

        with self.assertRaises(ValidationError):
            i2 = self.create_simple_invitation(mail_address="accepted@mail.com")
            i2.full_clean()
            i2.save()

    def test_valid_invite(self):
        """
            - tests that a new Invitation object won't be created if a valid, 
            i.e unexpired and unaccepted, Invitation already exists for the same mail
        """
        i = self.create_simple_invitation(mail_address="valid@mail.com")
        i.full_clean()
        i.save()

        with self.assertRaises(ValidationError):
            i2 = self.create_simple_invitation(mail_address="valid@mail.com")
            i2.full_clean()
            i2.save()

    def test_expired_invite(self):
        """
            - tests that a new Invitation object is created if an unaccepted 
            and expired Invitation exists for the same mail
        """
        # create an expired invite
        i = self.create_simple_invitation(
            mail_address="expired@mail.com", 
            sent_at=utils.get_expired_invitation_time(),
        )
        i.full_clean()
        i.save()

        i2 = self.create_simple_invitation(mail_address="expired@mail.com")
        i2.full_clean()
        i2.save()

        # i and i2 will have different primary keys, thus indicating that a 
        # new invitation was generated
        self.assertNotEqual(i.pk, i2.pk)

        # we can also check that 'i' was deleted
        with self.assertRaises(ObjectDoesNotExist):
            Invitation.objects.get(id=i.pk)