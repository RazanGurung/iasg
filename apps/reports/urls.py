from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="reports_index"),
    path("clients-missing-banking/", views.missing_banking, name="report_missing_banking"),
    path("clients-missing-other/", views.missing_other, name="report_missing_other"),
    path("clients-services-listing/", views.services_listing, name="report_services_listing"),
]
