from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.list_projects),
    path('<str:project_name>/', views.project_details),
    path('<str:project_name>/update/', views.update_project),
    path('<str:project_name>/sites/', views.list_sites),
    path('<str:project_name>/site/<str:site_name>/', views.edit_site),
    path('<str:project_name>/site/<str:site_name>/commodities/', views.list_sites),
]