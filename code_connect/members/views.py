from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import MemberForm

def register(request):
    if request.method == "POST":
        form = MemberForm(request.POST)
        if form.is_valid():
            print("code:", form.cleaned_data['invitation_code'])
            form.save()
            return redirect('home:index')

    else:
        form = MemberForm()
        print("new form:", form)
    return render(request, "members/registeration.html", {'form': form})