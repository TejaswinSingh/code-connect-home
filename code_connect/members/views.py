from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .forms import MemberForm
from .models import Member, Invitation
from django.contrib.auth.decorators import login_required

def register(request):
    context = {}
    members = Member.objects.all().order_by('-date_joined')
    context['total'] = len(members)
    context['members'] = members[:10]

    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home:index')

    else:
        if invitation_code:= request.GET.get('invite', None):
            form = MemberForm(initial={'invitation_code':invitation_code})
        else:
            form = MemberForm()
    
    context['form'] = form
    return render(request, "members/registration.html", context)

@login_required(login_url="/admin/")
def generate_invitation(request):
    context = {}
    if not request.user.has_perm('members.add_invitation'):
        return render(request, "error.html", {'error_code': "404 (Unauthorised)",'error': "We are extremely sorry, but you don't have the permission to generate invites 😔"}, status=401)
    if request.method == "POST":
        try:
            invitation = Invitation(user=request.user)
            invitation.full_clean()
            invitation.save()
            context['invitation_code'] = invitation.code
            context['post'] = True
        except ValidationError as e:
            context['errors'] = e.error_dict['__all__'][0]
    

    return render(request, "members/generate_invitation.html", context)
