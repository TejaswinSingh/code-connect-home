from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from members.forms import MemberForm, InviteForm
from members.models import Member

from . import utils



#_____________________________________views___________________________________________


def register(request):
    """
        - allows requests with a valid invitation_code (and an invited mail) to register

        *   Anonymous user submits a form with various fields, two of them being invitation_code and
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
            # TODO: redirect to route to setup a user object
            return redirect('home:index')

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


@login_required(login_url="/admin/login/")
def invite(request):
    """
        - allows users with perm ('members.add_invitation') to send invites to a list of mails.

        *   The mails to be invited can be specified either through the text-area or by uploading 
            a .csv file containing the said mails.
        *   An Invitation object with a unique invite-code will be created for each mail specified. 
            A background task will then send invitations using the above objects.      
    """

    if not request.user.has_perm('members.add_invitation'):
        return render(
                request, 
                "error.html", 
                {
                    'error_code': "401 (Unauthorised)",
                    'error': "We are extremely sorry, but you don't have the permission to generate invites 😔"
                }, 
                status=401,
            )

    if request.method == "POST":
        form = InviteForm(request.POST, request.FILES)
        if form.is_valid():
            return render(request, "members/invite_page.html", {'form': InviteForm(), 'success': True})

    else:
        form = InviteForm()

    return render(request, "members/invite_page.html", {'form': form})