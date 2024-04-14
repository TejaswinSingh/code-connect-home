from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ObjectDoesNotExist, ValidationError
# from django.core.files import File

from members.forms import MemberForm, InviteForm
from members.models import Invitation, Member, CustomUser
from members import utils



class InviteFormTests(TestCase):
    """
        - tests for InviteForm

        NOTE: learn more about testing Django forms here-
        https://stackoverflow.com/questions/7304248/how-should-i-write-tests-for-forms-in-django

        and more about testing Django FileField here-
        https://stackoverflow.com/questions/4283933/what-is-the-clean-way-to-unittest-filefield-in-django
    """

    #_______________________utilities_________________________

    def create_simple_csv(self, name="test.csv", content=b'Sample text'):
        return SimpleUploadedFile(name, content)

    def create_simple_form(self, csv_file=None, mail_list=None):
        return InviteForm(
            data={'mail_list': mail_list}, 
            files={"csv_file": csv_file}
        )
    

    #_______________________tests_________________________

    def test_no_input(self):
        """
            - tests that atleast one of two inputs must be provided
        """
        form = self.create_simple_form()
        self.assertFormError(
            form, field=None, 
            errors=["No input provided."]
        )
      
    def test_file_extension(self):
        """
            - tests that file (if provided) has a .csv extension
        """
        file = self.create_simple_csv(name="hello.txt")
        form = self.create_simple_form(csv_file=file)
        self.assertFormError(
            form, field='csv_file', 
            errors=["Invalid file format. Please upload a CSV file."]
        )

    def test_email_column(self):
        """
            - tests that CSV file has an `email` column
        """
        file = self.create_simple_csv(
            name='email_column.csv',
            content=b'name, age, marks'
        )
        form = self.create_simple_form(csv_file=file)
        self.assertFormError(
            form, field='csv_file', 
            errors=["Error processing CSV file. No 'email' column was found."]
        )

    def test_no_mails(self):
        """
            - tests that CSV file must have atleast one mail address
        """
        file = self.create_simple_csv(
            name='no_mails.csv',
            content=b'name, email, marks\njohn, , 84.67'
        )
        form = self.create_simple_form(csv_file=file)
        self.assertFormError(
            form, field='csv_file', 
            errors=["No mail addresses were found in the file."]
        )
        
    def test_invalid_mail_address(self):
        """
            - tests that mail addresses provided are in correct format.
            Also, If even a single mail is not valid, then no mails will be saved.
        """
        file = self.create_simple_csv(
            name='mail_address.csv',
            content=b'name, email, marks\nOliver, oliver23@mail.com, 99.67\njohn, john@, 84.67'
        )
        form = self.create_simple_form(csv_file=file, mail_list='example@mail.com')
        self.assertFormError(
            form, field=None, 
            errors=["john@ - ['Enter a valid email address.']"]
        )   

        # as we can check, the other two mails were not saved
        for mail in ['oliver23@mail.com', 'example@mail.com']:
            q = Invitation.objects.filter(mail_address=mail)
            self.assertEqual(len(q), 0)

    def test_repeated_mails(self):
        """
            - tests that if a mail address is provided more than one time, then it is only
            taken once.

            NOTE: no error will be generated in this case
        """
        file = self.create_simple_csv(
            name='repeated_mails.csv',
            content=b'name, email, marks\nUnknown, repeated@mail.com, 84.67'
        )
        form = self.create_simple_form(
            csv_file=file, 
            mail_list='unrepeated@mail.com, repeated@mail.com'
        )
        
        # 'repeated@mail.com' was provided twice, but only gets saved once
        if form.is_valid():
            q = Invitation.objects.filter(mail_address='repeated@mail.com')
            self.assertEqual(len(q), 1)
        else:
            raise ValidationError(f"{form.errors}")

    def test_accepted_invite(self):
        """
            - tests that if an invitation sent to a mail was accepted, then
            another invitation can't be created for that mail.
        """
        form = self.create_simple_form(mail_list='accepted@mail.com')
        if form.is_valid():
            i = Invitation.objects.get(mail_address='accepted@mail.com')
            i.accepted = True   # Mark the invitation as accepted 
            i.full_clean()
            i.save()

            # try to create another invitation with the same mail
            form = self.create_simple_form(mail_list='accepted@mail.com')
            self.assertFormError(
                form, field=None, 
                errors=["accepted@mail.com - ['This mail has already accepted an Invitation before.']"]
            )
        else:
            raise ValidationError(f"{form.errors}")

    def test_unexpired_invite(self):
        """
            - tests that a new invitation is not created if a valid, i.e unexpired
            and unaccepted, invitation already exists for the provided mail.
        """
        form = self.create_simple_form(mail_list='unexpired@mail.com')
        if form.is_valid():

            # try to create another invitation with the same mail
            form = self.create_simple_form(mail_list='unexpired@mail.com')
            self.assertFormError(
                form, field=None, 
                errors=["unexpired@mail.com - ['A valid invitation already exists for this mail.']"]
            )
        else:
            raise ValidationError(f"{form.errors}")

    def test_expired_invite(self):
        """
            - tests that a new invitation is created if any prior invitation
            sent to an mail was not accepted and has now expired. The first invitation
            will be deleted.
        """
        form = self.create_simple_form(mail_list='expired@mail.com')
        if form.is_valid():
            i = Invitation.objects.get(mail_address='expired@mail.com')
            i.sent_at = utils.get_expired_invitation_time() # Make the invitation expired
            i.full_clean()
            i.save()

            # try to create another invitation with the same mail
            form = self.create_simple_form(mail_list='expired@mail.com')
            if form.is_valid():
                i2 = Invitation.objects.get(mail_address='expired@mail.com')

                # i and i2 will have different primary keys, thus indicating that a 
                # new invitation was generated
                self.assertNotEqual(i.pk, i2.pk)

                # we can also check that 'i' was deleted
                with self.assertRaises(ObjectDoesNotExist):
                    Invitation.objects.get(id=i.pk)
        else:
            raise ValidationError(f"{form.errors}")
                    


class MemberFormTests(TestCase):
    """ Tests for MemberForm """

    #_______________________utilities_________________________
 
    def create_simple_form(
        self,
        firstname="John", lastname="Carter",
        email="johncarter001@dev.cs", roll="22BECSE44", contact="+91 9999999999",
        programme="CSE", semester="4", invitation_code=''
    ):
        
        fields = {
            'firstname': firstname, 
            'lastname': lastname, 
            'email': email,
            'roll': roll,
            'contact': contact,
            'programme': programme,
            'semester': semester,
            'invitation_code': invitation_code
        }
        return MemberForm(fields)
    

    #_______________________tests_________________________

    def test_invalid_invitation_code(self):
        """
            - tests that invalid invitation codes are not accepted
        """
        form = self.create_simple_form(invitation_code='INVALID')
        self.assertFormError(
            form, field='invitation_code', 
            errors=["Invalid invitation code! Please contact club authorities for more information."]
        )

    def test_uninvited_email(self):
        """
            - tests that uninvited mails can be used for
            registration.
        """
        i = Invitation(mail_address='invited@mail.edu')
        i.full_clean()
        i.save()
        form = self.create_simple_form(invitation_code=i.code, email='uninvited@mail.edu')
        self.assertFormError(
            form, field='email', 
            errors=["This email wasn't sent an invitation."]
        )

    def test_accepted_invitation(self):
        """
            - tests that accepted invitations can't be used
            again.
        """
        i = Invitation(mail_address='accepted@mail.edu')
        i.accepted = True
        i.full_clean()
        i.save()
        form = self.create_simple_form(invitation_code=i.code, email=i.mail_address)
        self.assertFormError(
            form, field='invitation_code', 
            errors=["This invitation code was already accepted! Please contact club authorities if this was not done by you."]
        )

    def test_expired_invitation(self):
        """
            - tests that expired invitations can't be used for
            registration.
        """
        i = Invitation(
            mail_address='expired@mail.edu',
            sent_at=utils.get_expired_invitation_time()
        )
        i.full_clean()
        i.save()
        form = self.create_simple_form(invitation_code=i.code, email=i.mail_address)
        self.assertFormError(
            form, field='invitation_code', 
            errors=["This invitation code has expired! Please contact club authorities to request a new one."]
        )

    def test_invitation_was_accepted(self):
        """
            - tests that the Invitation object has property {accepted} = True
            after the registration was complete
        """
        i = Invitation(mail_address='example@mail.edu')
        i.full_clean()
        i.save()
        self.assertEqual(i.accepted, False)
        form = self.create_simple_form(invitation_code=i.code, email=i.mail_address)
        if form.is_valid():
            form.save()
            # refetch the updated object `i` from db
            i = Invitation.objects.get(mail_address=i.mail_address)
            self.assertEqual(i.accepted, True)
        else:
            raise ValidationError(f"{form.errors}")

    def test_member_object_was_created(self):
        """
            - tests that a Member object is created on successfull
            registration.
        """
        i = Invitation(mail_address='example@mail.edu')
        i.full_clean()
        i.save()
        form = self.create_simple_form(invitation_code=i.code, email=i.mail_address)
        if form.is_valid():
            form.save()
            # if a Member object was not found, then ObjectDoesNotExist error 
            # would have been raised
            Member.objects.get(email=i.mail_address)
        else:
            raise ValidationError(f"{form.errors}")

    def test_customuser_object_was_created(self):
        """
            - tests that a CustomUser object refrenced by Member.user is
            created on successfull registration.
        """
        i = Invitation(mail_address='example@mail.edu')
        i.full_clean()
        i.save()
        form = self.create_simple_form(invitation_code=i.code, email=i.mail_address)
        if form.is_valid():
            form.save()
            m = Member.objects.get(email=i.mail_address)
            u = CustomUser.objects.get(email=i.mail_address)
            self.assertEqual(m.user, u)
        else:
            raise ValidationError(f"{form.errors}")

    def test_wrong_roll_format(self):
        """
            - tests that only roll(s) matching the roll format of the 
            provided programme must be accepted
        """
        i = Invitation(mail_address='example@mail.edu')
        i.full_clean()
        i.save()
        form = self.create_simple_form(invitation_code=i.code, email=i.mail_address, roll="22BECSE44", programme='ECE')
        self.assertFormError(
            form, field='roll', 
            errors=["Roll number doesn't match the roll-format of the selected programme."]
        )

        # no error should be raised here
        form = self.create_simple_form(invitation_code=i.code, email=i.mail_address, roll="22BECSE44", programme='CSE')
        if not form.is_valid():
            raise ValidationError(f"{form.errors}")