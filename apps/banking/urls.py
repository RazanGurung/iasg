from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="banking_index"),
]
