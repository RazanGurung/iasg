from django.urls import path

from . import views

urlpatterns = [
    path("reveal/<str:field_id>/", views.reveal, name="security_reveal"),
]
