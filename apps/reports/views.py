from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.clients.models import Client


@login_required
def index(request):
    return render(request, "core/stub.html", {"title": "Reports"})


@login_required
def missing_banking(request):
    clients = [
        c for c in Client.objects.filter(active=True).order_by("name")
        if not c.bank_name or not c.routing_number or not c.account_number
    ]
    return render(request, "reports/client_list.html", {
        "title": "Clients missing banking info",
        "columns": ["Client", "Bank name", "Routing #", "Account #"],
        "rows": [[c.name, c.bank_name or "—", "on file" if c.routing_number else "—",
                  "on file" if c.account_number else "—"] for c in clients],
    })


@login_required
def missing_other(request):
    clients = [
        c for c in Client.objects.filter(active=True).order_by("name")
        if not c.federal_id or not c.state_id or not c.county or not c.phone or not c.email
    ]
    return render(request, "reports/client_list.html", {
        "title": "Clients missing other info",
        "columns": ["Client", "Federal ID", "State ID", "County", "Phone", "Email"],
        "rows": [[c.name, c.federal_id or "—", c.state_id or "—", c.county or "—",
                  c.phone or "—", c.email or "—"] for c in clients],
    })


@login_required
def services_listing(request):
    clients = Client.objects.filter(active=True).order_by("name")
    return render(request, "reports/client_list.html", {
        "title": "Clients services listing",
        "columns": ["Client", "Sales tax", "Payroll", "Taxes / other", "Cig / tobacco"],
        "rows": [[c.name, "Yes" if c.sales_tax else "No", "Yes" if c.payroll else "No",
                  "Yes" if c.taxes_other else "No", "Yes" if c.cig_tob else "No"] for c in clients],
    })
