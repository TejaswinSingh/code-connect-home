from django.urls import path
from .import views

app_name = "members"

urlpatterns = [
    path("registration/", views.register, name="member_registration"),
    path("generateInvite/", views.generate_invitation, name="generate_invitation"),
]