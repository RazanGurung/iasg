import datetime
import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.clients.models import Client

from .models import SalesTaxEntry

_CENTS = Decimal("0.01")
_MONTH_NAMES = ["", "January", "February", "March", "April", "May", "June",
                "July", "August", "September", "October", "November", "December"]


def _money(value):
    return value.quantize(_CENTS, rounding=ROUND_HALF_UP)


def _fmt(value):
    return f"{value:,.2f}"


def _fmt0(value):
    return "0" if value == 0 else _fmt(value)


def _pct(rate):
    return f"{rate:.4f}".rstrip("0").rstrip(".") or "0"


def _dec(value):
    try:
        return Decimal(value or "0")
    except InvalidOperation:
        return Decimal("0")


@login_required
def batch(request):
    year = int(request.GET.get("year", 2026))
    month = int(request.GET.get("month", 8))

    if request.method == "POST" and request.POST.get("action") == "regenerate":
        for client in Client.objects.filter(sales_tax=True):
            SalesTaxEntry.objects.get_or_create(client=client, year=year, month=month)
        return redirect(f"{reverse('salestax_batch')}?year={year}&month={month}")

    entries = SalesTaxEntry.objects.filter(year=year, month=month).select_related("client")
    rows = []
    for e in entries:
        client = e.client
        state_rate, county_rate, city_rate, special_rate = (
            _dec(client.state_rate), _dec(client.county_rate),
            _dec(client.city_rate), _dec(client.special_rate),
        )
        sales_d, exempt_d = _dec(e.total_sales), _dec(e.exempt)
        taxable = sales_d - exempt_d

        amt_state = _money(taxable * state_rate)
        amt_county = _money(taxable * county_rate)
        amt_city = _money(taxable * city_rate)
        amt_special = _money(taxable * special_rate)
        meal_amt = _money(_dec(e.meal_tax))
        payable = _money(amt_state + amt_county + amt_city + amt_special)

        rows.append({
            "entry_id": e.id, "name": client.name, "county": client.county, "state": client.state,
            "filed": e.filed, "mode": e.pay_mode,
            "fed_id": client.federal_id, "state_id": client.state_id,
            "state_rate": _pct(state_rate), "county_rate": _pct(county_rate),
            "city_rate": _pct(city_rate), "special_rate": _pct(special_rate),
            "sales": _fmt0(sales_d), "exempt": _fmt0(exempt_d),
            "amt_state": _fmt0(amt_state), "amt_county": _fmt0(amt_county),
            "amt_city": _fmt0(amt_city), "amt_special": _fmt0(amt_special),
            "meal_amt": _fmt0(meal_amt), "payable": _fmt0(payable),
            "submit_date": e.submit_date,
            "routing_field_id": f"{e.id}-routing",
            "routing_masked": f"•••••{client.routing_number[-4:]}" if client.routing_number else "—",
            "routing_reveal_url": reverse("security_reveal", args=[f"salestax-{e.id}-routing"]),
            "account_field_id": f"{e.id}-account",
            "account_masked": f"••••{client.account_number[-4:]}" if client.account_number else "—",
            "account_reveal_url": reverse("security_reveal", args=[f"salestax-{e.id}-account"]),
            "save_url": reverse("salestax_entry_save", args=[e.id]),
            "rates_json": json.dumps({
                "st": float(state_rate), "co": float(county_rate),
                "ci": float(city_rate), "sp": float(special_rate),
            }),
        })
    rows.sort(key=lambda r: r["name"])

    filed_count = sum(1 for r in rows if r["filed"])
    return render(request, "salestax/batch.html", {
        "rows": rows,
        "year": year, "month": month, "month_name": _MONTH_NAMES[month],
        "years": [2025, 2026],
        "months": [(i, name) for i, name in enumerate(_MONTH_NAMES) if i],
        "client_count": len(rows),
        "filed_count": filed_count,
        "open_count": len(rows) - filed_count,
        "states": sorted({r["state"] for r in rows}),
    })


@login_required
def entry_save(request, entry_id):
    entry = get_object_or_404(SalesTaxEntry, pk=entry_id)
    if request.method == "POST":
        entry.total_sales = request.POST.get("sales", "0").replace(",", "").strip() or "0"
        entry.exempt = request.POST.get("exempt", "0").replace(",", "").strip() or "0"
        entry.meal_tax = request.POST.get("meal_tax", "0").replace(",", "").strip() or "0"
        entry.pay_mode = request.POST.get("pay_mode", "").strip()
        was_filed = entry.filed
        entry.filed = _dec(entry.total_sales) > 0
        if entry.filed and not was_filed:
            today = datetime.date.today()
            entry.submit_date = f"{today.day} {today.strftime('%b %Y')}"
        entry.save()
    return redirect(f"{reverse('salestax_batch')}?year={entry.year}&month={entry.month}")
