from django.urls import path

from . import views

urlpatterns = [
    path("", views.batch, name="salestax_batch"),
    path("entry/<int:entry_id>/save/", views.entry_save, name="salestax_entry_save"),
    path("entry/<int:entry_id>/details/", views.entry_details, name="salestax_entry_details"),
]
