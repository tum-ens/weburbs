from django.urls import path

from . import views

urlpatterns = [
    path('projects/', views.list_projects),
    path('project/<str:project_name>/', views.project_details),
    path('project/<str:project_name>/update/', views.update_project),
    path('project/<str:project_name>/sites/', views.list_sites),
    path('project/<str:project_name>/site/<str:site_name>/', views.edit_site),
    path('project/<str:project_name>/site/<str:site_name>/commodities/', views.list_sites),
]