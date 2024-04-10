from django.urls import path
from .import views

app_name = "members"

urlpatterns = [
    path("registration/", views.register, name="member_registration"),
    path("invite/", views.invite, name="invite"),
]