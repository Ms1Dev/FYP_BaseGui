
from django.urls import path
from . import views


urlpatterns=[
    path('', views.Index, name="index"),
    path('index', views.Index, name="index")
]
