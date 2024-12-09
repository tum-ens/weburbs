from django.urls import path

from projects.api import (
    simulate,
)

urlpatterns = [
    path("simulation/<uuid:simid>/", simulate.report_simulation),
]
