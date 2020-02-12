from django.conf.urls import url
from django.views import View
from . import views

urlpatterns = [
    #127.0.0.1:8000/v1/users
    url(r'/GET/$', views.get_stocks),
    url(r'/total', views.get_total),
]
