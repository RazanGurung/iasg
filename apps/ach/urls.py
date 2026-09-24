from django.urls import path

from . import views

urlpatterns = [
    path("monthly-fees/", views.monthly_fees, name="ach_monthly_fees"),
    path("monthly-fees/export/", views.monthly_fees_csv, name="ach_monthly_fees_csv"),
]
