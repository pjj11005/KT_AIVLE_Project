# blog/urls.py
from django.urls import path
from django.contrib import admin
from . import views

app_name = 'selfchatgpt'
urlpatterns = [
    path('', views.index, name='index'),
]
