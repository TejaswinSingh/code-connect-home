from django.db import models
#from django.contrib.auth.models import User
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
import string
import random
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ObjectDoesNotExist


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


###########################################################################################


class CustomUser(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    default_password = "12345678"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


###########################################################################################


class Member(models.Model):
    """
        - represents a club member.

        *   Each Member should ideally be associated with a CustomUser for logging into
            their account.
        *   Only Member's in the 8th {semester} can have {has_graduated} set to True
        *   The {roll} field should match the roll format of the selected {programme} 
    """ 
    
    #______________________field choices_________________________

    # Programme
    CSE = {'tag': "CSE", 'roll_fmt': "BECSE", 'name': "Computer Science & Engineering"}
    CCS = {'tag': "CCS", 'roll_fmt': "BECCS", 'name': "Computer Science & Cyber Security"}
    ECE = {'tag': "ECE", 'roll_fmt': "BEECE", 'name': "Electronics and Communication Engineering"}
    AVI = {'tag': "AVI", 'roll_fmt': "BEAVI", 'name': "Avionics"}
    PROGRAMMES = [CSE, CCS, ECE, AVI]
    PROGRAMME_CHOICES= {prog['tag']: prog['name'] for prog in PROGRAMMES}

    # Semester
    SEMESTER_CHOICES = [
        ("1", "1st Semester"), ("2", "2nd Semester"),
        ("3", "3rd Semester"), ("4", "4th Semester"),
        ("5", "5th Semester"), ("6", "6th Semester"),
        ("7", "7th Semester"), ("8", "8th Semester"),
    ]
    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*


    #______________________field utility functions_________________________

    def profile_pic_path(instance, filename):
        """ Format profile pic path """
        return f'members/{instance.programme}/{instance.date_joined.strftime("%Y")}/sem{instance.semester}/{filename}'
    
    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*


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
    about = models.CharField(max_length=256, blank=True, help_text="Tell others about yourself")
    contact = PhoneNumberField(null=False, blank=False, unique=True, help_text="eg. +91 96XXXXXXX", verbose_name="phone number")
    date_joined = models.DateTimeField(auto_now_add=True)
    has_graduated = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to=profile_pic_path, max_length=500, default='defaults/profile.png')

    # Fields with choices
    programme = models.CharField(max_length=3, choices=PROGRAMME_CHOICES, null=False, blank=False, default='')
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=False, blank=False, default='')

    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*


    def save(self, *args, **kwargs):
        """
            - custom save method 

            *   before creating a Member object, creates a CustomUser object first with
                same firstname, lastname and email attributes and a default password
        """  
        if not self.user:  # if user is not assigned already
            user = CustomUser(first_name=self.firstname, last_name=self.lastname, email=self.email, password=CustomUser.default_password)
            user.full_clean()
            user.save()
            self.user = user  # refer the newly created CustomUser object to this Member object
        super().save(*args, **kwargs)  # Call the "real" save() method.


    #______________________model validation_________________________

    def clean(self):
        """
            - Custom clean method
        """
        def is_valid_format(input_str, constant_part):
            """ checks if the input_str contains the constant_part """
            pattern = re.compile(r'^\d{2}(' + re.escape(constant_part) + r')\d{2}$', re.IGNORECASE)
            return bool(pattern.match(input_str))
        
        def check_roll(self):
            """ checks if the roll number matches the roll format of the selected programme  """
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
        can_graduate(self)
        check_roll(self)

    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*



    #______________________instance methods_________________________

    def full_name(self):
        """ fullname of the Member """
        return f'{self.firstname} {self.lastname}'

    def __str__(self):
        return self.full_name()
    
    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*


###########################################################################################


class Invitation(models.Model):
    """
        - represents the invitation object that is used for inviting each member

        *   code: unique str value starting with 'CUJ' of CODE_LENGTH characters.
            Required for verification at the time of Member registration.
        *   mail_address: this is where the Invitation will be sent. Must be unique as well.
        *   timestamp: auto-generated at the time of object creation.
        *   sent_at: notes when the invitation was sent to the mail_address.
        *   accepted: True if user has registered with a Member account, otherwise False 
        
        NOTE: each (code, mail-address) pair is unique, and while registering via a particular 
        invite code, the user can only use the mail associated with that code.
    """

    #______________________fixed_________________________

    VALID_DURATION = timedelta(days=7)
    CODE_LENGTH = 10

    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*


    #______________________model-fields_________________________

    code = models.CharField(max_length=CODE_LENGTH, blank=True, unique=True)
    mail_address = models.EmailField(max_length=100, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    accepted = models.BooleanField(default=False)

    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*



    #______________________instance methods_________________________

    def __str__(self):
        """ eg: 'Invite generated on 23-03-24 12:09:07 for example@mail.com' """
        return f"Invite generated on {timezone.localtime(self.timestamp).strftime('%d-%m-%y %I:%M:%S')} for {self.mail_address}"


    def has_expired(self):
        """ returns True if the given object has expired """
        if not self.sent_at: # if invitation exists but was not sent yet
            return False
        if timezone.now() - self.sent_at >= self.VALID_DURATION:
            return True
        return False

    #______________________________________________________________________________


    #______________________class methods_________________________

    def same_mail_exists(mail):
        """
            Returns that object if a Member object with the given mail address already exists. 
        """
        try:       
            return Member.objects.get(email=mail)
        except (ObjectDoesNotExist):
            return False
    
    def clean_db():
        """ deletes all expired and unaccepted objects """
        for invite in Invitation.objects.all():
            if invite.has_expired() and not invite.accepted:
                invite.delete()
    #______________________________________________________________________________


    #______________________model-level validation_________________________

    def clean(self):
        """
            - custom clean method

            *   fills 'code' field for each object
        """
        def get_random_string(length=6, chars=string.ascii_uppercase +string.digits):
            """ generates pseudo random strings of required length  """
            return ''.join(random.choice(chars) for _ in range(length))
        
        def generate_code():
            """ keep generating random strings until you get a unique one """
            while True:
                self.code = 'CUJ' + get_random_string(self.CODE_LENGTH - 3)
                if not Invitation.objects.filter(code=self.code).all():
                    break

        self.clean_mail_address()
        super().clean() # always call this method

        try:
            Invitation.objects.get(mail_address=self.mail_address)
            # only generate code at the time of object creation
        except ObjectDoesNotExist:
            generate_code()            
        
    
    def clean_mail_address(self):
        try:
            invite = Invitation.objects.get(mail_address=self.mail_address)
            if invite == self:
                return
        except ObjectDoesNotExist:
            return
        if invite.accepted:
            raise ValidationError(
                {"mail_address": _("A Member with this mail already exists!")}
            )
        else:   # not accepted
            if invite.has_expired():
                invite.delete() # delete the expired invite, so that a new one can be generated
            else: # not expired
                raise ValidationError(
                    {"mail_address": _("A valid invitation already exists for this mail.")}
                )

    #__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*__*