from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings

from datetime import timedelta
import os

from members.models import Invitation


#_______________________utilities_________________________

def permission_required(perm):
    """
        - a decorator used for checking if the user has the specified
        permission. If not then a 403 Forbidden status code is returned
        along with the error page.

        NOTE: no need to use @login_required before using this decorator.
    """
    def decorator(func):
        @login_required(login_url=settings.LOGIN_URL)
        def wrapper(request, *args, **kwargs):
            if not request.user.has_perm(perm):
                return render(
                        request, 
                        "error.html", 
                        {
                            'error_code': "403 (Forbidden)",
                            'error': "We are extremely sorry, but you don't have the permission to generate invites 😔"
                        }, 
                        status=403,
                    )
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def handle_uploaded_file(f):
    """ 
        - saves the user-uploaded file which is in memory to disk and 
        returns the file path. 
    """
    directory = f"invite_csv_files/"
    os.makedirs(directory, exist_ok=True)

    original_filename = f.name.replace(' ', '_')
    file_path = os.path.join(directory, original_filename)
    
    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path

def get_Invitation_or_None(code):
    """ rarely needed utility for Invitation model """
    try:
        invite = Invitation.objects.get(code=code)
        return invite
    except Exception:
        return Invitation(mail_address='')
    
def get_expired_invitation_time():
    """ 
        - returns a datetime object that is guaranteed to have an expired 
        Invitation time if checked at that moment 
    """
    return (timezone.now()-Invitation.VALID_DURATION-timedelta(hours=1))