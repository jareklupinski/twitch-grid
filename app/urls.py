from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('magic', views.magic, name='magic'),
]