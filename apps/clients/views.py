import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.salestax.models import SalesTaxEntry
from apps.worklists.models import StatusChange, Task

from .models import AnnualLiability, BankStatement, Client, Contact, Credential, Note

_TABS = [
    ("notes", "Notes"), ("credentials", "Credentials"), ("comms", "Communications"),
    ("salestax", "Sales Tax History"), ("tasks", "Tasks"), ("changes", "Additions / Closures"),
    ("bank", "Bank Statements"), ("annuals", "Annuals"), ("fin", "Financial Statements"),
    ("fn", "Functions & Reports"),
]


def _who(request):
    return request.user.get_username() or "—"


def _now():
    now = datetime.datetime.now()
    return now.strftime("%d %b %Y"), now.strftime("%I:%M %p").lstrip("0")


def _back(pk, tab):
    return f"{reverse('client_detail', args=[pk])}?tab={tab}"


def _mask(value, keep=4):
    value = value or ""
    if len(value) <= keep:
        return "•" * len(value)
    return "•" * (len(value) - keep) + value[-keep:]


@login_required
def client_new(request):
    if request.method == "POST":
        client = Client.objects.create(
            type=request.POST.get("type", "").strip() or "S-Corp",
            name=request.POST.get("name", "").strip() or "Unnamed client",
            dba=request.POST.get("dba", "").strip(),
            address1=request.POST.get("address1", "").strip(),
            address2=request.POST.get("address2", "").strip(),
            city=request.POST.get("city", "").strip(),
            state=request.POST.get("state", "").strip(),
            zip=request.POST.get("zip", "").strip(),
            county=request.POST.get("county", "").strip(),
            phone=request.POST.get("phone", "").strip(),
            email=request.POST.get("email", "").strip(),
            federal_id=request.POST.get("federal_id", "").strip(),
            start_date=request.POST.get("start_date", "").strip() or datetime.date.today().strftime("%d %b %Y"),
            state_id=request.POST.get("state_id", "").strip(),
            st_rate=request.POST.get("st_rate", "").strip(),
            withholding_sos_id=request.POST.get("withholding_id", "").strip(),
            sos_id_value=request.POST.get("sos_id", "").strip(),
            unmp_id=request.POST.get("unmp_id", "").strip(),
            unmp_rate=request.POST.get("unmp_rate", "").strip(),
            bank_name=request.POST.get("bank_name", "").strip(),
            routing_number=request.POST.get("routing_number", "").strip(),
            account_number=request.POST.get("account_number", "").strip(),
            sales_tax="svc_st" in request.POST,
            payroll="svc_payroll" in request.POST,
            taxes_other="svc_other" in request.POST,
            cig_tob="svc_cig" in request.POST,
            active=True,
        )
        contact_name = request.POST.get("contact_name", "").strip()
        if contact_name:
            Contact.objects.create(
                client=client, name=contact_name,
                email=request.POST.get("contact_email", "").strip(),
                phone=request.POST.get("contact_phone", "").strip(),
                ssn=request.POST.get("contact_ssn", "").strip(),
                drivers_license=request.POST.get("contact_dl", "").strip(),
                dob=request.POST.get("contact_dob", "").strip(),
                pct=request.POST.get("contact_pct", "").strip(),
                is_owner="contact_owner" in request.POST,
                receives_email="contact_rcpt" in request.POST,
            )
        return HttpResponse(status=204, headers={"HX-Redirect": reverse("client_detail", args=[client.id])})
    return render(request, "clients/new_client_form.html", {
        "today": datetime.date.today().strftime("%d %b %Y"),
    })


@login_required
def client_edit(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        for field in ("type", "name", "dba", "address1", "address2", "city", "state", "zip",
                      "county", "phone", "email", "date_closed"):
            if field in request.POST:
                setattr(client, field, request.POST.get(field, "").strip())
        client.active = "active" in request.POST
        client.closed = "closed" in request.POST
        client.sales_tax = "sales_tax" in request.POST
        client.payroll = "payroll" in request.POST
        client.taxes_other = "taxes_other" in request.POST
        client.cig_tob = "cig_tob" in request.POST
        client.save()
    return redirect(_back(pk, request.GET.get("tab", "notes")))


@login_required
def client_detail(request, pk):
    client = Client.objects.filter(pk=pk).first()
    if client is None:
        return render(request, "core/stub.html", {
            "title": f"Client {pk} not found.",
        })

    valid_keys = {k for k, _ in _TABS}
    active_tab = request.GET.get("tab", "notes")
    if active_tab not in valid_keys:
        active_tab = "notes"

    client.routing_masked = _mask(client.routing_number, keep=4)
    client.account_masked = _mask(client.account_number, keep=4)

    contacts = list(client.contact_set.all())
    contact_param = request.GET.get("contact")
    primary_contact = None
    if contact_param:
        primary_contact = next((c for c in contacts if str(c.id) == contact_param), None)
    if primary_contact is None:
        primary_contact = contacts[0] if contacts else None

    reveal_urls = {
        name: reverse("security_reveal", args=[f"client-{pk}-{name}"])
        for name in ("routing", "account")
    }
    if primary_contact:
        primary_contact.ssn_masked = _mask(primary_contact.ssn, keep=4)
        primary_contact.dl_masked = _mask(primary_contact.drivers_license, keep=0)
        primary_contact.dob_masked = _mask(primary_contact.dob, keep=0)
        for name in ("ssn", "dl", "dob"):
            reveal_urls[name] = reverse("security_reveal", args=[f"client-{pk}-contact-{primary_contact.id}-{name}"])

    credentials = list(client.credential_set.all())
    for cred in credentials:
        cred.field_id = f"cred-{cred.id}-password"
        cred.password_masked = _mask(cred.password, keep=0)
        cred.reveal_url = reverse("security_reveal", args=[f"client-{pk}-cred-{cred.id}-password"])

    notes_columns = [
        {"label": "Category"}, {"label": "Note"}, {"label": "Date"}, {"label": "Time"},
        {"label": "By"}, {"label": "Mod date"}, {"label": "Mod time"}, {"label": "ModBy"},
    ]
    notes = list(client.note_set.all())
    notes_rows = [{
        "selected": i == 0, "id": n.id,
        "cells": [
            {"value": n.category}, {"value": n.text}, {"value": n.date},
            {"value": n.time}, {"value": n.by}, {"value": n.mod_date},
            {"value": n.mod_time}, {"value": n.mod_by},
        ],
    } for i, n in enumerate(notes)]

    comms_columns = [{"label": v} for v in ("Type", "Content", "Date", "Time", "By")]
    comms_rows = [{"selected": False, "cells": [{"value": v} for v in row]} for row in [
        ["Email", f"Monthly statement email sent to {client.email}", "01 Sep 2026", "08:03 AM", "system"],
        ["Email", f"Monthly statement email sent to {client.email}", "01 Aug 2026", "08:01 AM", "system"],
    ]]

    _month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    salestax_columns = [{"label": v} for v in (
        "Year", "Month", "Status", "Total sales", "Exempt", "Pay mode", "Submit date")]
    salestax_rows = [{
        "selected": False,
        "cells": [
            {"value": e.year}, {"value": _month_names[e.month]},
            {"value": "Filed" if e.filed else "Open"}, {"value": e.total_sales, "num": True},
            {"value": e.exempt, "num": True}, {"value": e.pay_mode}, {"value": e.submit_date},
        ],
    } for e in client.salestax_entries.order_by("-year", "-month")]

    tasks = list(Task.objects.filter(client=client))
    tasks_columns = [{"label": v} for v in (
        "Task", "Notes", "Assigned on", "Assigned by", "Assigned to", "Due date", "Completed")]
    tasks_rows = [{
        "selected": False, "id": t.id,
        "cells": [
            {"value": t.task}, {"value": t.notes}, {"value": t.assigned_on}, {"value": t.assigned_by},
            {"value": t.assigned_to}, {"value": t.due_date}, {"value": "Yes" if t.completed else "No"},
        ],
    } for t in tasks]
    tasks_filters = [
        {"label": "Current client", "checked": True},
        {"label": "My tasks", "checked": False},
        {"label": "All tasks", "checked": False},
    ]

    changes = list(StatusChange.objects.filter(client=client))
    changes_columns = [{"label": v} for v in (
        "Status", "Start date", "Close date", "Notes", "Payroll", "Sales tax", "Taxes", "Added by")]
    changes_rows = [{
        "selected": False, "id": c.id,
        "cells": [
            {"value": c.status}, {"value": c.start_date}, {"value": c.close_date}, {"value": c.notes},
            {"value": "Yes" if c.payroll else "No"}, {"value": "Yes" if c.sales_tax else "No"},
            {"value": "Yes" if c.taxes_other else "No"}, {"value": c.added_by},
        ],
    } for c in changes]
    changes_filters = [
        {"label": "All clients", "checked": True},
        {"label": "Corporations", "checked": False},
        {"label": "Individuals", "checked": False},
    ]

    bank_statements = list(client.bank_statement_set.all())
    bank_filters = [
        {"label": "Current year", "checked": True},
        {"label": "Completed", "checked": False},
        {"label": "All years", "checked": False},
    ]

    annual_liabilities = list(client.annual_set.all())
    annuals_filters = [
        {"label": "Current year", "checked": True},
        {"label": "All years", "checked": False},
        {"label": "Completed", "checked": False},
    ]

    today = datetime.date.today()
    month_start = today.replace(day=1)
    next_month = (month_start.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    month_end = next_month - datetime.timedelta(days=1)
    fin_date_range = {
        "start": f"{month_start.day} {month_start.strftime('%b %Y')}",
        "end": f"{month_end.day} {month_end.strftime('%b %Y')}",
    }

    all_clients = Client.objects.order_by("name")
    ids = list(all_clients.values_list("id", flat=True))
    idx = ids.index(client.id) if client.id in ids else 0
    nav = {
        "first": ids[0] if ids else client.id,
        "prev": ids[idx - 1] if idx > 0 else client.id,
        "next": ids[idx + 1] if idx < len(ids) - 1 else client.id,
        "last": ids[-1] if ids else client.id,
    }

    return render(request, "clients/console.html", {
        "client": client,
        "contacts": contacts,
        "primary_contact": primary_contact,
        "all_clients": all_clients,
        "nav": nav,
        "tabs": [{"key": k, "label": label} for k, label in _TABS],
        "active_tab": active_tab,
        "active_tab_label": dict(_TABS)[active_tab],
        "reveal_urls": reveal_urls,
        "credentials": credentials,
        "notes_columns": notes_columns,
        "notes_rows": notes_rows,
        "comms_columns": comms_columns,
        "comms_rows": comms_rows,
        "salestax_columns": salestax_columns,
        "salestax_rows": salestax_rows,
        "tasks_columns": tasks_columns,
        "tasks_rows": tasks_rows,
        "tasks_filters": tasks_filters,
        "changes_columns": changes_columns,
        "changes_rows": changes_rows,
        "changes_filters": changes_filters,
        "bank_statements": bank_statements,
        "bank_filters": bank_filters,
        "annual_liabilities": annual_liabilities,
        "annuals_filters": annuals_filters,
        "fin_date_range": fin_date_range,
    })


@login_required
def client_panel(request, pk, tab):
    return render(request, "core/stub.html", {"title": f"Client {pk} — {tab}"})


@login_required
def client_summary(request, pk):
    client = get_object_or_404(Client, pk=pk)
    client.routing_masked = _mask(client.routing_number, keep=4)
    client.account_masked = _mask(client.account_number, keep=4)
    owner = client.contact_set.filter(is_owner=True).first() or client.contact_set.first()
    combined_rate = sum(
        float(v) for v in (client.state_rate, client.county_rate, client.city_rate, client.special_rate)
        if v
    )
    reveal_urls = {
        name: reverse("security_reveal", args=[f"client-{pk}-{name}"])
        for name in ("routing", "account")
    }
    if owner:
        reveal_urls["ssn"] = reverse("security_reveal", args=[f"client-{pk}-contact-{owner.id}-ssn"])
        reveal_urls["dl"] = reverse("security_reveal", args=[f"client-{pk}-contact-{owner.id}-dl"])
        owner.ssn_masked = _mask(owner.ssn, keep=4)
        owner.dl_masked = _mask(owner.drivers_license, keep=0)
    return render(request, "clients/summary.html", {
        "client": client, "owner": owner, "combined_rate": f"{combined_rate:.4f}".rstrip("0").rstrip("."),
        "reveal_urls": reveal_urls,
    })


# ---------------------------------------------------------------- Contacts

@login_required
def contact_save(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        contact_id = request.POST.get("contact_id")
        contact = get_object_or_404(Contact, pk=contact_id, client=client) if contact_id else Contact(client=client)
        contact.name = request.POST.get("name", "").strip()
        contact.email = request.POST.get("email", "").strip()
        contact.phone = request.POST.get("phone", "").strip()
        contact.pct = request.POST.get("pct", "").strip()
        contact.receives_email = "receives_email" in request.POST
        contact.is_owner = "is_owner" in request.POST
        if request.POST.get("ssn"):
            contact.ssn = request.POST.get("ssn", "").strip()
        if request.POST.get("dl"):
            contact.drivers_license = request.POST.get("dl", "").strip()
        if request.POST.get("dob"):
            contact.dob = request.POST.get("dob", "").strip()
        contact.save()
    return redirect(_back(pk, request.POST.get("tab", "notes")))


@login_required
def contact_delete(request, pk, contact_id):
    if request.method == "POST":
        Contact.objects.filter(pk=contact_id, client_id=pk).delete()
    return redirect(_back(pk, request.POST.get("tab", "notes")))


# -------------------------------------------------------------------- Notes

@login_required
def note_save(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        note_id = request.POST.get("note_id")
        text = request.POST.get("text", "").strip()
        if text:
            date, time = _now()
            if note_id:
                note = get_object_or_404(Note, pk=note_id, client=client)
                note.category = request.POST.get("category", "General")
                note.text = text
                note.mod_date, note.mod_time = date, time
                note.mod_by = _who(request)
                note.save()
            else:
                Note.objects.create(
                    client=client, category=request.POST.get("category", "General"),
                    text=text, date=date, time=time, by=_who(request),
                )
    return redirect(_back(pk, "notes"))


@login_required
def note_delete(request, pk, note_id):
    if request.method == "POST":
        Note.objects.filter(pk=note_id, client_id=pk).delete()
    return redirect(_back(pk, "notes"))


# ------------------------------------------------------------- Credentials

@login_required
def credential_save(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        cred_id = request.POST.get("credential_id")
        cred = get_object_or_404(Credential, pk=cred_id, client=client) if cred_id else Credential(client=client)
        cred.site = request.POST.get("site", "").strip()
        cred.username = request.POST.get("username", "").strip()
        if request.POST.get("password"):
            cred.password = request.POST.get("password", "").strip()
        cred.notes = request.POST.get("notes", "").strip()
        cred.active = "active" in request.POST
        if cred.site:
            cred.save()
    return redirect(_back(pk, "credentials"))


@login_required
def credential_delete(request, pk, credential_id):
    if request.method == "POST":
        Credential.objects.filter(pk=credential_id, client_id=pk).delete()
    return redirect(_back(pk, "credentials"))


# ---------------------------------------------------------- Bank statements

@login_required
def bank_statement_save(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        stmt = get_object_or_404(BankStatement, pk=request.POST.get("statement_id"), client=client)
        stmt.notes = request.POST.get("notes", "").strip()
        stmt.received_stored = "received_stored" in request.POST
        stmt.check_image_received = "check_image_received" in request.POST
        stmt.date_received = request.POST.get("date_received", "").strip()
        stmt.received_by = request.POST.get("received_by", "").strip()
        stmt.data_entered = "data_entered" in request.POST
        stmt.entered_by = request.POST.get("entered_by", "").strip()
        stmt.date_completed = request.POST.get("date_completed", "").strip()
        stmt.save()
    return redirect(_back(pk, "bank"))


@login_required
def bank_statement_delete(request, pk, statement_id):
    if request.method == "POST":
        BankStatement.objects.filter(pk=statement_id, client_id=pk).delete()
    return redirect(_back(pk, "bank"))


# ---------------------------------------------------------------- Annuals

@login_required
def annual_save(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        annual = get_object_or_404(AnnualLiability, pk=request.POST.get("annual_id"), client=client)
        annual.filed = "filed" in request.POST
        annual.requirement_received = "requirement_received" in request.POST
        annual.completed = "completed" in request.POST
        annual.date_filed = request.POST.get("date_filed", "").strip()
        annual.filed_by = request.POST.get("filed_by", "").strip()
        annual.save()
    return redirect(_back(pk, "annuals"))


@login_required
def annual_delete(request, pk, annual_id):
    if request.method == "POST":
        AnnualLiability.objects.filter(pk=annual_id, client_id=pk).delete()
    return redirect(_back(pk, "annuals"))
