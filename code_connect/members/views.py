from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import MemberForm
from .models import Member

def register(request):
    context = {}
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            print("code:", form.cleaned_data['invitation_code'])
            form.save()
            return redirect('home:index')

    else:
        if invitation_code:= request.GET.get('invite', None):
            form = MemberForm(initial={'invitation_code':invitation_code})
        else:
            form = MemberForm()
        members = Member.objects.all().order_by('-date_joined')
        context['total'] = len(members)
        context['members'] = members[:5]
    
    context['form'] = form
    return render(request, "members/registeration.html", context)