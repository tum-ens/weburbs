from django.urls import path

from . import views

urlpatterns = [
    path("csrf/", views.get_csrf, name="security-csrf"),
    path("login/", views.loginUser, name="security-login"),
    path("logout/", views.logoutUser, name="security-logout"),
    path("session/", views.session, name="security-session"),
    path("presence/", views.presence, name="security-presence"),
    path("me/", views.me, name="security-me"),
    path("register/", views.register, name="security-session"),
    path("pending/", views.pending_users, name="security-pending-users"),
    path("users/", views.list_users, name="security-list-users"),
    path("approve/<str:username>/", views.approve_user, name="security-approve-user"),
    path("reject/<str:username>/", views.reject_user, name="security-reject-user"),
    path(
        "delete/<str:username>/",
        views.delete_user_permanently,
        name="security-delete-user",
    ),
    path(
        "running_simulations/",
        views.running_simulations,
        name="security-running-simulations",
    ),
    path(
        "running_simulations/<uuid:simid>/stop/",
        views.admin_stop_simulation,
        name="security-admin-stop-simulation",
    ),
    path(
        "verify_mail/<str:username>/<uuid:token>/",
        views.verify_mail,
        name="security-session",
    ),
    path("resend_token/<str:username>/", views.resend_mail, name="security-session"),
    path(
        "request_password_reset/",
        views.request_password_reset,
        name="security-request-password-reset",
    ),
    path(
        "reset_password/<str:username>/<uuid:token>/",
        views.reset_password,
        name="security-reset-password",
    ),
]
