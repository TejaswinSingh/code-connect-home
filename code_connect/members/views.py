from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings

from members.forms import MemberForm, InviteForm
from members.models import Member, CustomUser

from . import utils
from .utils import permission_required



#_____________________________________views___________________________________________


def register(request):
    """
        - allows requests with a valid invitation_code (and an invited mail) to register

        *   User submits a form with various fields, two of them being invitation_code and
            email. We validate both of them against the Invitation model and only if an object is found,
            the user is allowed to register. Other fields also have their own custom validation defined 
            in either MemberForm (forms.py) or Member (models.py) class.
        *   If the form is valid, then corresponding Member and CustomUser objects are created with the
            Member.user model-field referencing CustomUser through a One-One relationship.
            Member is used for storing user attributes, whereas CustomUser is for authentication 
            and authorisation tasks.     
    """

    # displays the last 10 people who registered
    members = Member.objects.all().order_by('-date_joined')
    context = {'total': len(members), 'members': members[:10]}

    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            
            # authenticate the newly created user and then
            # redirect to "account/password-setup/" route
            user = authenticate(email=form.cleaned_data['email'], password=CustomUser.DEFAULT_PASSWORD)
            if user:
                login(request, user)
            return redirect('members:setup-password')

    else:
        #   * autofill 'invitation_code' and 'email' form-fields if query parameter 
        #   * 'i' is provided.
        if invitation_code:= request.GET.get('i', None):
            invite = utils.get_Invitation_or_None(code=invitation_code)
            form = MemberForm(initial={'invitation_code':invitation_code, 'email': invite.mail_address})
        else:
            form = MemberForm()
    
    context['form'] = form
    return render(request, "members/registration.html", context)


@permission_required('members.add_invitation')
def invite(request):
    """
        - allows users with perm ('members.add_invitation') to send invites to a list of mails.

        *   The mails to be invited can be specified either through the text-area or by uploading 
            a .csv file containing the said mails.
        *   An Invitation object with a unique invite-code will be created for each mail specified. 
            A background task will then send invitations via mail.      
    """

    if request.method == "POST":
        form = InviteForm(request.POST, request.FILES)
        if form.is_valid():
            return render(request, "members/invite_page.html", {'form': InviteForm(), 'success': True})

    else:
        form = InviteForm()

    return render(request, "members/invite_page.html", {'form': form})


@login_required(login_url=settings.LOGIN_URL)
def profile(request):
    if hasattr(request.user, 'member'):
        return render(request, "members/profile_page.html", {'member': request.user.member})
    return HttpResponse(f'{request.user} is not a member')
    # return HttpResponse(f'Profile of {request.user}')