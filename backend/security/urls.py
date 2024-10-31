from django.urls import path

from . import views

urlpatterns = [
    path('csrf/', views.get_csrf, name='security-csrf'),
    path('login/', views.login_view, name='security-login'),
    path('logout/', views.logout_view, name='security-logout'),
    path('session/', views.session_view, name='security-session'),
]