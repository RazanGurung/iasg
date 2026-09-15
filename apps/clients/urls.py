from django.urls import path

from . import views

urlpatterns = [
    path("new/", views.client_new, name="client_new"),
    path("<int:pk>/", views.client_detail, name="client_detail"),
    path("<int:pk>/panel/<slug:tab>/", views.client_panel, name="client_panel"),
    path("<int:pk>/edit/", views.client_edit, name="client_edit"),
    path("<int:pk>/summary/", views.client_summary, name="client_summary"),

    path("<int:pk>/contacts/save/", views.contact_save, name="contact_save"),
    path("<int:pk>/contacts/<int:contact_id>/delete/", views.contact_delete, name="contact_delete"),

    path("<int:pk>/notes/save/", views.note_save, name="note_save"),
    path("<int:pk>/notes/<int:note_id>/delete/", views.note_delete, name="note_delete"),

    path("<int:pk>/credentials/save/", views.credential_save, name="credential_save"),
    path("<int:pk>/credentials/<int:credential_id>/delete/", views.credential_delete, name="credential_delete"),

    path("<int:pk>/bank/save/", views.bank_statement_save, name="bank_statement_save"),
    path("<int:pk>/bank/<int:statement_id>/delete/", views.bank_statement_delete, name="bank_statement_delete"),

    path("<int:pk>/annuals/save/", views.annual_save, name="annual_save"),
    path("<int:pk>/annuals/<int:annual_id>/delete/", views.annual_delete, name="annual_delete"),
]
