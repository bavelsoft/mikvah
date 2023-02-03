from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('times', views.times, name='times'),
    path('schedule', views.schedule, name='schedule'),
    path('attendant', views.attendant, name='attendant'),
]
