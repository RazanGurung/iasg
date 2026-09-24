import csv
import datetime
import logging
from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from apps.clients.models import Client

logger = logging.getLogger("apps.ach.monthly_fees")

_MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]


def _dec(value):
    try:
        return Decimal(value or "0")
    except InvalidOperation:
        return Decimal("0")


def _rows(request):
    """Clients due an ACH debit this run: active, not closed, banking info
    on file, and a fee greater than zero. public/21.webp is the reference —
    routing #, account #, company name capped at 22 characters, a literal
    "C" (transaction/account-type code — every sample row has it), the fee
    in cents with no decimal point (standard ACH convention), and an id
    string. The id's trailing number in the legacy file was the Access
    AutoNumber; here it's Client.id (docs/open-questions.md — not a
    confirmed match to any legacy value)."""
    year = int(request.GET.get("year", datetime.date.today().year))
    month = int(request.GET.get("month", datetime.date.today().month))

    clients = (
        Client.objects.filter(active=True, closed=False)
        .exclude(routing_number="").exclude(account_number="")
        .order_by("name")
    )

    rows = []
    total = Decimal("0")
    for c in clients:
        fee = _dec(c.monthly_fee)
        if fee <= 0:
            continue
        cents = int((fee * 100).to_integral_value())
        rows.append({
            "routing_number": c.routing_number,
            "account_number": c.account_number,
            "company_name": c.name[:22],
            "type_code": "C",
            "fee_display": f"{fee:.2f}",
            "fee_cents": cents,
            "client_ref": f"S_{year}_{month}_{c.id}",
        })
        total += fee

    return year, month, rows, total


@login_required
def monthly_fees(request):
    year, month, rows, total = _rows(request)
    return render(request, "ach/monthly_fees.html", {
        "year": year, "month": month, "month_name": _MONTH_NAMES[month],
        "rows": rows, "client_count": len(rows), "total": f"{total:,.2f}",
    })


@login_required
def monthly_fees_csv(request):
    year, month, rows, total = _rows(request)

    logger.info(
        "ACH monthly fees file generated: period=%s-%02d clients=%d total=%s generated_by=%s",
        year, month, len(rows), f"{total:.2f}", request.user,
    )

    response = HttpResponse(content_type="text/csv")
    filename = f"monthly_fees_{year}_{month:02d}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    for r in rows:
        writer.writerow([
            r["routing_number"], r["account_number"], r["company_name"],
            r["type_code"], r["fee_cents"], r["client_ref"],
        ])
    return response
