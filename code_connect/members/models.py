from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from home.models import SendInviteTask

import re
import string
import random
from datetime import timedelta

#_______________________________________models___________________________________________

# NOTE: refer below for Custom User model using email rather than username for authentication
# https://www.fomfus.com/articles/how-to-use-email-as-username-for-django-authentication-removing-the-username/

class UserManager(BaseUserManager):
    """ Define a model manager for User model with no username field. """

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """ Create and save a User with the given email and password. """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """ Create and save a regular User with the given email and password. """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """ Create and save a SuperUser with the given email and password. """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)



class CustomUser(AbstractUser):
    """ User model. """

    username = None
    email = models.EmailField(_('email address'), unique=True)

    default_password = "12345678"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()



class Member(models.Model):
    """
        - represents a club member.

        *   Each Member should ideally be associated with a CustomUser for logging into
            their account.
        *   Only Member's in the 8th {semester} can have {has_graduated} set to True
        *   The {roll} field should match the roll format of the selected {programme} 
    """ 

    #______________________field choices_________________________

    CSE = {'tag': "CSE", 'roll_fmt': "BECSE", 'name': "Computer Science & Engineering"}
    CCS = {'tag': "CCS", 'roll_fmt': "BECCS", 'name': "Computer Science & Cyber Security"}
    ECE = {'tag': "ECE", 'roll_fmt': "BEECE", 'name': "Electronics and Communication Engineering"}
    AVI = {'tag': "AVI", 'roll_fmt': "BEAVI", 'name': "Avionics"}
    PROGRAMMES = [CSE, CCS, ECE, AVI]
    PROGRAMME_CHOICES= {prog['tag']: prog['name'] for prog in PROGRAMMES}

    SEMESTER = [
        ("1", "1st Semester"), ("2", "2nd Semester"),
        ("3", "3rd Semester"), ("4", "4th Semester"),
        ("5", "5th Semester"), ("6", "6th Semester"),
        ("7", "7th Semester"), ("8", "8th Semester"),
    ]
    SEMESTER_CHOICES = {sem[0]: sem[1] for sem in SEMESTER}


    #______________________field utility functions_________________________

    def profile_pic_path(instance, filename):
        """ Format profile pic path """
        return f'members/{instance.programme}/{instance.date_joined.strftime("%Y")}/sem{instance.semester}/{filename}'
    

    #______________________model-fields_________________________
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="member",
    )
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    roll = models.CharField(max_length=10, unique=True, verbose_name="roll number")
    about = models.CharField(
        max_length=256, blank=True, 
        help_text="Tell others about yourself"
    )
    contact = PhoneNumberField(
        null=False, blank=False, unique=True, 
        help_text="eg. +91 96XXXXXXX", verbose_name="phone number"
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    has_graduated = models.BooleanField(default=False)
    profile_pic = models.ImageField(
        upload_to=profile_pic_path, max_length=500, 
        default='defaults/profile.png'
    )

    # Fields with choices
    programme = models.CharField(
        max_length=3, choices=PROGRAMME_CHOICES, 
        null=False, blank=False, default=''
    )
    semester = models.CharField(
        max_length=1, choices=SEMESTER_CHOICES, 
        null=False, blank=False, default=''
    )


    #______________________model validation_________________________

    def save(self, *args, **kwargs):
        """
            - custom save method 

            *   before saving a Member object, creates a CustomUser object first with
                same firstname, lastname and email attributes and a default password
        """  
        # if user is not assigned already, then create a new CustomUser object
        # and refer it to to this Member's user field
        if not self.user:  
            user = CustomUser(
                first_name=self.firstname, last_name=self.lastname, 
                email=self.email, password=CustomUser.default_password
            )
            user.full_clean()
            user.save()
            self.user = user 
        super().save(*args, **kwargs)  # Call the "real" save() method.

    def clean(self):
        """ Custom clean method """

        #______________________inner functions_________________________

        def is_valid_format(input_str, constant_part):
            """ checks if the input_str contains the constant_part """
            pattern = re.compile(r'^\d{2}(' + re.escape(constant_part) + r')\d{2}$', re.IGNORECASE)
            return bool(pattern.match(input_str))
        
        def check_roll(self):
            """ checks if the roll number matches the roll format of the selected programme """
            for prog in self.PROGRAMMES:
                if prog['tag'] == self.programme:
                    if not is_valid_format(self.roll, prog['roll_fmt']):
                        raise ValidationError(
                            {"roll": _("Roll number doesn't match the roll-format of the selected programme.")}
                        )
                    break
        
        def can_graduate(self):
            """ checks if Member is allowed to graduate """
            if self.has_graduated and not self.semester == "8":
                raise ValidationError(
                        {"has_graduated": _("Students that are not in the 8th semester can't be marked as graduated.")}
                    )

        super().clean() # always call this method
        self.roll = self.roll.upper()
        can_graduate(self)
        check_roll(self)


    #______________________instance methods_________________________

    def full_name(self):
        """ fullname of the Member """
        return f'{self.firstname} {self.lastname}'

    def __str__(self):
        return self.full_name()



class Invitation(models.Model):
    """
        - represents the invitation object that is used for inviting each member

        *   code: unique str value starting with 'CUJ' of CODE_LENGTH characters.
            Required for verification at the time of Member registration.
        *   mail_address: this is where the Invitation will be sent. Must be unique as well.
        *   timestamp: auto-generated at the time of object creation.
        *   sent_at: notes when the invitation was actually sent to the mail_address.
        *   accepted: True if user has accepted the invite and created a Member account, otherwise False 
        
        NOTE: each (code, mail-address) pair is unique, and while registering via a particular 
        invite code, the user can only use the mail associated with that code.
    """

    #______________________const_________________________

    VALID_DURATION = timedelta(days=7)
    CODE_LENGTH = 10


    #______________________model-fields_________________________

    code = models.CharField(max_length=CODE_LENGTH, blank=True, unique=True)
    mail_address = models.EmailField(max_length=100, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    accepted = models.BooleanField(default=False)


    #______________________instance methods_________________________

    def __str__(self):
        """ eg: 'Invite generated on 23-03-24 12:09:07 for example@mail.com' """
        return f"Invite generated on {timezone.localtime(self.timestamp).strftime('%d-%m-%y %I:%M:%S')} for {self.mail_address}"

    def has_expired(self):
        """ returns True if the given object has expired """
        if not self.sent_at: # if invitation exists but is not sent yet
            return False
        if timezone.now() - self.sent_at >= self.VALID_DURATION:
            return True
        return False
    
    def save(self, *args, **kwargs):
        """
            - custom save method 

            *   after saving the Invitation, we create a SendEmail task
            that is responsible for actually sending the invitation mail to
            the provided {mail_address}
        """  
        super().save(*args, **kwargs)  # Call the "real" save() method.

        # create task only the first time when the Invitation was created
        if not self.sent_at:
            task = SendInviteTask(
                name=f"Invitation to {self.mail_address}",
                invite=self
            )
            task.full_clean()
            task.save()
            # NOTE: {sent_at} is updated when the invitation is actually sent using 
            # SendInviteTask.send() method




    #______________________class methods_________________________
    
    def clean_db():
        """ deletes all expired Invitations that were not accepted """
        for invite in Invitation.objects.all():
            if invite.has_expired() and not invite.accepted:
                invite.delete()


    #______________________model-level validation_________________________

    def clean(self):
        """
            - custom clean method

            *   fills 'code' field with randomly generated strings
        """

        #______________________inner functions_________________________

        def get_random_string(length=6, chars=string.ascii_uppercase+string.digits):
            """ generates pseudo random strings of required length  """
            return ''.join(random.choice(chars) for _ in range(length))
        
        def generate_code():
            """ keep generating random strings until you get a unique one """
            while True:
                self.code = 'CUJ' + get_random_string(self.CODE_LENGTH - 3)
                if not Invitation.objects.filter(code=self.code).all():
                    break

        self.clean_check_for_existing()
        super().clean() # always call this method
        try:
            Invitation.objects.get(mail_address=self.mail_address)
            # only generate code at the time of object creation
        except ObjectDoesNotExist:
            generate_code()            
        
    def clean_check_for_existing(self):
        """
            - handles the case when an Invitation object already exists
            for the provided mail. Three cases can arise:
                1) The invitation was accepted. In this case, we can't allow another
                    invitation to be generated for the same mail.
                2) The invitation was not accepted and -
                    i) has now expired. Here, we will delete the existing invitation, 
                    so that a new one can be generated. 
                    ii) is still valid. Thus another invitation object can't be 
                    generated until the first one expires.
        """
        try:
            invite = Invitation.objects.get(mail_address=self.mail_address)
            if invite == self:
                return
        except ObjectDoesNotExist:
            return
        if invite.accepted:
            raise ValidationError(
                {"mail_address": _("This mail has already accepted an Invitation before.")}
            )
        else:   
            if invite.has_expired():
                invite.delete() # delete the expired invite, so that a new one can be generated
            else:
                raise ValidationError(
                    {"mail_address": _("A valid invitation already exists for this mail.")}
                )
