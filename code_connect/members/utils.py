from .models import Invitation
import os


def handle_uploaded_file(f):
    '''
        - saves the user-uploaded file which is in memory to disk and returns the file path.
    '''
    directory = f"invite_csv_files/"
    os.makedirs(directory, exist_ok=True)

    original_filename = f.name.replace(' ', '_')
    file_path = os.path.join(directory, original_filename)
    
    with open(file_path, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path



def get_Invitation_or_None(code):
    '''
        - randomly needed utility
    '''
    try:
        invite = Invitation.objects.get(code=code)
        return invite
    except Exception:
        return Invitation(mail_address='')