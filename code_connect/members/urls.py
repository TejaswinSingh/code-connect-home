from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from members import views
from members.models import CustomUser

app_name = "members"

urlpatterns = [
    path("registration/", views.register, name="member_registration"),
    path("invite/", views.invite, name="invite"),
    path(
        "account/setup-password/", 
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy('members:profile'), 
            template_name='members/password-setup.html', 
            extra_context={'old_password': CustomUser.DEFAULT_PASSWORD}
        ), 
        name="setup-password"
    ),
    path("profile/", views.profile, name="profile"),
]