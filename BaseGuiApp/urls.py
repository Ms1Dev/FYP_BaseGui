
from django.urls import path
from . import views


urlpatterns=[
    path('', views.Index, name="index"),
    path('index', views.Index, name="index"),
    path('log-out', views.Logout, name="log-out"),
    path('user-login', views.Login, name="user-login")
]
