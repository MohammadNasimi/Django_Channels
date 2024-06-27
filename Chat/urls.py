from django.urls import path

from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path('login', LoginView.as_view(template_name='chat/login.html'), name="login")
]