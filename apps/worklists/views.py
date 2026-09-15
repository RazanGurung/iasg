import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.clients.models import Client

from .models import StatusChange, Task


@login_required
def tasks(request):
    return render(request, "core/stub.html", {"title": "Tasks — firm-wide worklist (open a client to add one)"})


@login_required
def additions_closures(request):
    return render(request, "core/stub.html", {
        "title": "Additions & closures — firm-wide log (open a client to add one)",
    })


def _back(pk):
    return f"{reverse('client_detail', args=[pk])}?tab=tasks"


@login_required
def task_save(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        task_text = request.POST.get("task", "").strip()
        task = get_object_or_404(Task, pk=task_id, client=client) if task_id else Task(client=client)
        if task_text:
            task.task = task_text
            task.notes = request.POST.get("notes", "").strip()
            task.assigned_by = request.POST.get("assigned_by", "").strip() or request.user.get_username()
            task.assigned_to = request.POST.get("assigned_to", "").strip()
            task.due_date = request.POST.get("due_date", "").strip()
            task.assigned_on = task.assigned_on or datetime.date.today().strftime("%d %b %Y")
            task.completed = "completed" in request.POST
            task.save()
    return redirect(_back(pk))


@login_required
def task_delete(request, pk, task_id):
    if request.method == "POST":
        Task.objects.filter(pk=task_id, client_id=pk).delete()
    return redirect(_back(pk))


@login_required
def change_save(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == "POST":
        change_id = request.POST.get("change_id")
        change = get_object_or_404(StatusChange, pk=change_id, client=client) if change_id else StatusChange(client=client)
        change.status = request.POST.get("status", "Addition")
        change.start_date = request.POST.get("start_date", "").strip()
        change.close_date = request.POST.get("close_date", "").strip()
        change.notes = request.POST.get("notes", "").strip()
        change.payroll = "payroll" in request.POST
        change.sales_tax = "sales_tax" in request.POST
        change.taxes_other = "taxes_other" in request.POST
        change.added_by = request.user.get_username()
        change.save()
    return redirect(f"{reverse('client_detail', args=[pk])}?tab=changes")


@login_required
def change_delete(request, pk, change_id):
    if request.method == "POST":
        StatusChange.objects.filter(pk=change_id, client_id=pk).delete()
    return redirect(f"{reverse('client_detail', args=[pk])}?tab=changes")
