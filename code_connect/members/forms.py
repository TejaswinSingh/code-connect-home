from .models import Member, Invitation
from django.forms import ModelForm, ValidationError
from django import forms
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

class MemberForm(ModelForm):
    template_name = "members/memberForm.html"
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

    def __init__(self, *args, **kwargs):
        super(MemberForm, self).__init__(*args, **kwargs)

        # Set default value and placeholder for the programme field
        self.fields['programme'].choices = [('', 'Please select Programme/Department')] + list(self.fields['programme'].choices)

        # Set default value and placeholder for the semester field
        self.fields['semester'].choices = [('', 'Please select Semester')] + list(self.fields['semester'].choices)


    def clean_invitation_code(self):
        data = self.cleaned_data["invitation_code"]

        try:
            Invitation.objects.get(code=data)
        except (ObjectDoesNotExist):
            raise ValidationError("Invalid invitation code! Please contact club leaders for more information.")

        return data