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


class CustomUser(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Member(models.Model):

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

    # Fields with choices

    CSE = {'tag': "CSE", 'roll_fmt': "BECSE", 'name': "Computer Science & Engineering"}
    CCS = {'tag': "CCS", 'roll_fmt': "BECCS", 'name': "Computer Science & Cyber Security"}
    ECE = {'tag': "ECE", 'roll_fmt': "BEECE", 'name': "Electronics and Communication Engineering"}
    AVI = {'tag': "AVI", 'roll_fmt': "BEAVI", 'name': "Avionics"}
    PROGRAMMES = [CSE, CCS, ECE, AVI]
    PROGRAMME_CHOICES= {prog['tag']: prog['name'] for prog in PROGRAMMES}
    programme = models.CharField(max_length=3, choices=PROGRAMME_CHOICES, null=False, blank=False, default='')

    SEMESTER_CHOICES = [
        ("1", "1st Semester"), ("2", "2nd Semester"),
        ("3", "3rd Semester"), ("4", "4th Semester"),
        ("5", "5th Semester"), ("6", "6th Semester"),
        ("7", "7th Semester"), ("8", "8th Semester"),
    ]
    semester = models.CharField(max_length=1, choices=SEMESTER_CHOICES, null=False, blank=False, default='')

    # profile pic
    def profile_pic_path(instance, filename):
        return f'members/{instance.programme}/{instance.date_joined.strftime("%Y")}/sem{instance.semester}/{filename}'
    
    profile_pic = models.ImageField(upload_to=profile_pic_path, max_length=500, default='defaults/profile.png')

    # model sanitization
    def clean(self):
        def is_valid_format(input_str, constant_part):
            pattern = re.compile(r'^\d{2}(' + re.escape(constant_part) + r')\d{2}$', re.IGNORECASE)
            return bool(pattern.match(input_str))
        
        def check_roll(self):
            for prog in self.PROGRAMMES:
                if prog['tag'] == self.programme:
                    if not is_valid_format(self.roll, prog['roll_fmt']):
                        raise ValidationError(
                            {"roll": _("Roll number doesn't match the roll-format of the selected programme.")}
                        )
                    break

        if self.has_graduated and not self.semester == "8":
            raise ValidationError(
                            {"has_graduated": _("Students that are not in the 8th semester can't be marked as graduated.")}
                        )
        check_roll(self)


    # instance methods
    def get_full_name(self):
        return f'{self.firstname} {self.lastname}'

    def __str__(self):
        return self.get_full_name()


class Invitation(models.Model):
    code = models.CharField(max_length=10, blank=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name="invites",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    VALID_DURATION = timedelta(days=3)
    MAX_OBJECTS = 3
    CODE_LENGTH = 10


    def clean(self):

        # generates pseudo random invites
        def generate_code(size=6, chars=string.ascii_uppercase +string.digits):
            return ''.join(random.choice(chars) for _ in range(size))
        
        # returns True if the passed invitation object is valid
        def is_valid(self, invite):
            if timezone.now() - invite.timestamp < self.VALID_DURATION:
                return True
            return False
            
        # deletes expired invitation objects
        def clean_db(self):
            for invite in Invitation.objects.all():
                if not is_valid(self, invite):
                    invite.delete()

        clean_db(self)
        if len(Invitation.objects.all()) == self.MAX_OBJECTS:
            raise ValidationError(_("More invitations can't be created. Delete previous invitations or wait for them to expire."))

        # keep generating code until you get a unique one
        while True:
            self.code = 'CUJ' + generate_code(self.CODE_LENGTH - 3)
            if not Invitation.objects.filter(code=self.code).all():
                break

    def __str__(self):
        return f"Invite code: {self.code} generated on {timezone.localtime(self.timestamp).strftime('%d-%m-%y at %I:%M:%S')}"