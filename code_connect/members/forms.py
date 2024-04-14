from django.forms import forms, ModelForm, ValidationError
from django import forms
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.translation import gettext_lazy as _

import os, csv
from . import utils

from .models import Member, Invitation



class MemberForm(ModelForm):
    """ form for Member registration page """

    # form template
    template_name = "members/memberForm.html"

    #_______________________form fields_________________________

    invitation_code = forms.CharField(max_length=10)
    class Meta:
        model = Member
        fields = [
            'firstname', 
            'lastname', 
            'email',
            'roll',
            'contact',
            'programme',
            'semester',
        ]

    #_______________________dunder methods_________________________
        
    def __init__(self, *args, **kwargs):
        """ Set default value and placeholder for the programme field & the semester field """
        super(MemberForm, self).__init__(*args, **kwargs)
        self.fields['programme'].choices = [('', 'Please select Programme/Department')] + list(self.fields['programme'].choices)
        self.fields['semester'].choices = [('', 'Please select Semester')] + list(self.fields['semester'].choices)


    #_______________________form-level validation_________________________

    def clean(self):
        """
            - custom clean method

            *   A ValidationError is raised in the following scenarios:  
                    i) If no Invitation object exists for the submitted invitation_code.
                    ii) If the email provided by the user doesn't match the email associated with the 
                    Invitation.
        """
        super().clean() # always call this method
        try:
            invite = Invitation.objects.get(code=self.cleaned_data.get("invitation_code"))
        except ObjectDoesNotExist:
            # no need to raise another exception here, if the Invite doesn't exist, a
            # ValidationError was already raised in clean_invitation_code
            return
        
        email = self.cleaned_data["email"]
        if invite.mail_address != email:
            raise ValidationError(
                {"email": _("This email wasn't sent an invitation.")}
            )

    def save(self, commit=True):
        """
            - Call this method after form validation is completed, and if `commit` is True 
            mark the Invitation object used for registration as accepted, to make sure the 
            same invitation cannot be used again. If `commit` is False then you need to update
            the related Invitation object yourself. 
        """
        m = super(MemberForm, self).save(commit=False)
        if commit:
            try:
                invite = Invitation.objects.get(code=self.cleaned_data.get("invitation_code"))
                invite.accepted = True
                invite.save()
            except ObjectDoesNotExist:
                pass
            m.save()
        return m


    #_______________________field-level validation_________________________
        
    def clean_invitation_code(self):
        """
            - custom clean for {invitation_code}

            *   A ValidationError is raised in the following scenarios: 
                i) If no Invitation object exists for the submitted invitation_code.
                ii) If the Invitation object was already accepted.
                iii) If the unaccepted Invitation object has expired
        """
        data = self.cleaned_data["invitation_code"]
        try:
            invite = Invitation.objects.get(code=data)
            if invite.accepted:
                raise ValidationError("This invitation code was already accepted! Please contact club authorities if this was not done by you.")
            else:  # if not accepted
                if invite.has_expired():
                    raise ValidationError("This invitation code has expired! Please contact club authorities to request a new one.")
                else:   # if not expired and not accepted, only then the field is valid
                    pass
        except (ObjectDoesNotExist):
            raise ValidationError("Invalid invitation code! Please contact club authorities for more information.")

        return data



class InviteForm(forms.Form):
    """
        - form that generates Invitation objects for the mails provided in the input

        *   User can use two types of inputs fields to submit mails- a csv file and a text-area. 
            Atleast one input needs to be submitted, while both can be submitted simultaneously too.
        *   The csv_file, if provided, must have an 'email' column. Mails addresses in text-area need to be
            delimited by a comma (,).
        *   Validation is done on each mail address at the Invitation model level. It checks that the mail
            is a valid email address while also maintaining the unique constraint.
        *   If even one mail address was found to be invalid, the others will not get stored to the 
            db either. The user must make sure all mails are valid.
        *   If a mail address is present in both the csv file and the text-area, then it is taken as a single
            entity and doesn't get repeated.
        *   If an Invitation object already exists for a provided mail address, then three things can happen-
                1) If the Invitation was accepted, i.e the recepient has registered as a Member using that mail,
                    then an error stating such is generated.
                2) If the Invitation was not accepted and-
                    i) it has now expired, then we delete that Invitation, and create a new one for the given mail address.
                    ii) it is not yet expired, then we raise an error stating such.  
    """
    
    # form template
    template_name = "members/inviteForm.html"

    #_______________________form fields_________________________

    csv_file = forms.FileField(required=False)
    mail_list = forms.CharField(required=False, min_length=1, widget=forms.Textarea)

    #_______________________form-level validation_________________________

    def clean(self):
        """
            - checks that atleast one input was provided and calls the function
                to create Invitation objects if no errors were found in field-level 
                validation.
        """
        super().clean()  # always call this method
        csv_file = self.cleaned_data.get("csv_file")
        mail_list = self.cleaned_data.get("mail_list")

        if not csv_file and not mail_list and not self.errors:
            raise ValidationError("No input provided.")
        
        if not self.errors:
            self.create_invites()

    #_______________________field-level validation_________________________

    def clean_csv_file(self):
        """
            - validates user uploaded file

            *   checks that file, if provided, has a .csv extension.
            *   for reading the in-memory-file, it is temporarily saved to disk by calling 
                handle_uploaded_file() which returns the file path.
            *   for further validation, it calls get_mails_from_csv(), which return a set of 
                extracted mails on successful validation. Though if an error occurs, a ValidationError 
                gets raised inside and will be propagated above.
        """
        csv_file = self.cleaned_data.get("csv_file")
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise ValidationError("Invalid file format. Please upload a CSV file.")
            
            csv_file_path = utils.handle_uploaded_file(csv_file)
            return InviteForm.get_mails_from_csv(csv_file_path)  # returns the set of extracted mails

        return csv_file  # always return the value you want this form-field to have when accessed again

    def clean_mail_list(self):
        """
            - validates the text-area input

            *   expects mail addresses to be separated by a comma (,)
            *   returns the set of non-empty mail-addresses found

            NOTE: validation of mail format is done at model level while creating Invitation objects in
            create_invites()
        """
        mails = set()
        mail_list = self.cleaned_data.get("mail_list")
        if mail_list:
            for mail in mail_list.split(','):
                mail = mail.strip()
                if mail:
                    mails.add(mail)
        return mails

    #_______________________helper functions_________________________

    def get_mails_from_csv(file):
        """
            - handles further validation of the uploaded csv_file.

            *   raises Validation error if:
                    1) No 'email' column was found in the file
                    2) No mail-addresses were found in the email column
                    3) Some other error occurs while reading the file
            *   returns the set of mails that were extracted
        """
        mails = set()
        if not file:
            return mails

        try:
            with open(file, "r") as f:
                # when `skipinitialspace` is True, whitespace immediately following the delimiter is ignored.
                csv_data = csv.DictReader(f, skipinitialspace=True)
                if 'email' not in csv_data.fieldnames:
                    raise ValueError
                for row in csv_data:
                    email = row['email'].strip()
                    if email:   # skip empty email records
                        mails.add(email)  
                if not mails:
                    raise TypeError
        except ValueError:
            os.remove(file)
            raise ValidationError("Error processing CSV file. No 'email' column was found.")
        except TypeError:
            os.remove(file)
            raise ValidationError("No mail addresses were found in the file.")
        except Exception:
            os.remove(file)
            raise ValidationError("Error processing CSV file. Check your file format.")
        
        os.remove(file)  # delete the file after you're done
        return mails

    def create_invites(self):
        """
            - creates an Invitation object for each mail-address provided.

            *   takes the union of the mail sets extracted from both the input fields
        """
        # mails from text-area
        if not (mails_list := self.cleaned_data.get("mail_list")):
            mails_list = set()
        # mails from csv file
        if not (mails_csv := self.cleaned_data.get("csv_file")):
            mails_csv = set()
        mails = mails_list | mails_csv  # union
        invites = []
        Invitation.clean_db()   # deletes all expired AND unaccepted invitations
        for mail in mails:
            try:
                invite = Invitation(mail_address=mail)
                invite.full_clean()
                invites.append(invite)
            except ValidationError as e:
                raise ValidationError(f"{mail} - {e.error_dict['mail_address'][0]}")
            
        #   * we haven't yet saved the objects to db. We wait until all of them have been created 
        #   * and have passed the model-validation checks
        for i in invites:
            i.save()
