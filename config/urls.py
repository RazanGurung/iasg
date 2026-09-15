from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("clients/", include("apps.clients.urls")),
    path("sales-tax/", include("apps.salestax.urls")),
    path("banking/", include("apps.banking.urls")),
    path("financials/", include("apps.financials.urls")),
    path("worklists/", include("apps.worklists.urls")),
    path("comms/", include("apps.comms.urls")),
    path("ach/", include("apps.ach.urls")),
    path("reports/", include("apps.reports.urls")),
    path("security/", include("apps.security.urls")),
]
