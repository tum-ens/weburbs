from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.create_project),
    path('list/', views.list_projects),
    path('details/<str:project_name>/update_globals/', views.update_globals),
    path('details/<str:project_name>/globals/', views.list_globals),
    path('details/<str:project_name>/create_site/', views.create_site),
    path('details/<str:project_name>/sites/', views.list_sites),
    path('details/<str:project_name>/site/<str:site_name>/update/', views.list_sites),
    path('details/<str:project_name>/site/<str:site_name>/commodities/', views.list_sites),
]