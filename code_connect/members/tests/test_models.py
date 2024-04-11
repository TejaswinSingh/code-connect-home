from django.test import TestCase, SimpleTestCase
from members.models import Member, CustomUser, Invitation
from django.core.exceptions import ValidationError, ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone
from datetime import timedelta

class MemberModelTests(TestCase):
    """
        Tests for Member
    """
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

    @classmethod
    def setUpTestData(cls):
        pass

    def test_roll_format(self):
        """
            - tests that roll matches the format of the selected programme
        """
        m = self.create_simple_member(roll='22beece23')
        with self.assertRaises(ValidationError):
            m.full_clean()

    def test_has_graduated(self):
        """
            - tests that only Member(s) in 8th Sem can have {has_graduated} set to True
        """
        with self.assertRaises(ValidationError):
            m = self.create_simple_member(has_graduated=True, semester='4')
            m.full_clean()

        # no error will be raised in this case
        m = self.create_simple_member(has_graduated=True, semester='8')
        m.full_clean()

    def test_user_is_created(self):
        """
            - tests that a CustomUser object is created if we call save() on a Member object
        """
        m = self.create_simple_member()
        m.full_clean()
        m.save()
        self.assertIsInstance(m.user, CustomUser)

    def test_default_profile_pic(self):
        """
            - tests that if a {profile_pic} is not provided, then a default one is created
        """
        m = self.create_simple_member()
        self.assertEqual(m.profile_pic, 'defaults/profile.png')



class InvitationModelTests(TestCase):
    """
        Tests for Invitation
    """
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
    
    def test_has_expired(self):
        """
            - tests `has_expired()` instance method
        """
        # create the i1 as if it was sent 8 days back and is thus now expired
        i = self.create_simple_invitation(sent_at=timezone.now() - timedelta(days=8))
        # valid invite i2
        i2 = self.create_simple_invitation(
            mail_address="example@mail.com", 
            sent_at=timezone.now() - timedelta(hours=4)
        )
        i.full_clean()
        i.save()
        i2.full_clean()
        i2.save()
        self.assertEqual(i.has_expired(), True)
        self.assertEqual(i2.has_expired(), False)

    def test_clean_db(self):
        """
            - tests `clean_db()` class method to see if it deletes expired and 
            unaccepted invites
        """
        i = self.create_simple_invitation(
            mail_address="expired@mail.edu",
            sent_at=timezone.now() - timedelta(days=8)
        )
        i.full_clean()
        i.save()
        Invitation.clean_db()
        with self.assertRaises(ObjectDoesNotExist):
            Invitation.objects.get(id=i.pk)

    def test_unique_code(self):
        """
            - tests that a unique {code} is generated for each Invitation object
        """
        i = self.create_simple_invitation(mail_address="unique@mail.com")
        i.full_clean()
        i.save()

        # if code is not unique then MultipleObjectsReturned error would be generated
        Invitation.objects.get(code=i.code) 

    def test_accepted(self):
        """
            - tests that a new Invitation object can't be created
            if an accepted Invitation for the same mail already exists
        """
        i = self.create_simple_invitation(mail_address="accepted@mail.com", accepted=True)
        i.full_clean()
        i.save()

        with self.assertRaises(ValidationError):
            i2 = self.create_simple_invitation(mail_address="accepted@mail.com")
            i2.full_clean()
            i2.save()

    def test_valid(self):
        """
            - tests that a new Invitation object can't be created
            if a valid Invitation for the same mail already exists
        """
        i = self.create_simple_invitation(mail_address="valid@mail.com")
        i.full_clean()
        i.save()

        with self.assertRaises(ValidationError):
            i2 = self.create_simple_invitation(mail_address="valid@mail.com")
            i2.full_clean()
            i2.save()

    def test_expired(self):
        """
            - tests that a new Invitation object is created
            if an unaccepted Invitation for the same mail exists and has now expired
        """
        # create an expired invite
        i = self.create_simple_invitation(
            mail_address="expired@mail.com", 
            sent_at=timezone.now() - timedelta(days=8),
        )
        i.full_clean()
        i.save()

        i2 = self.create_simple_invitation(mail_address="expired@mail.com")
        i2.full_clean()
        i2.save()

        # i and i2 will have different primary keys, thus indicating a new invite is generated
        self.assertNotEqual(i.pk, i2.pk)

        # we can also confirm that 'i' is now deleted
        with self.assertRaises(ObjectDoesNotExist):
            Invitation.objects.get(id=i.pk)