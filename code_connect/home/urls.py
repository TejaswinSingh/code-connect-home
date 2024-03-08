from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
	path("", views.index, name="index"),
    path("member/registration/", views.register, name="member_registration"),
]
