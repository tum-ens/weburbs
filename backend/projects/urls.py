from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.create_project, name='security-session'),
    path('list/', views.list_projects, name='security-session'),
]