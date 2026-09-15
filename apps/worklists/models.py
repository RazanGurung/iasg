from django.db import models

from apps.clients.models import Client

# Prototype-only, managed=False (see apps/clients/models.py header). Tasks and
# status changes are firm-wide in the legacy app (not owned by one client),
# but each row may optionally reference a client.


class Task(models.Model):
    client = models.ForeignKey(Client, related_name="task_set", on_delete=models.CASCADE, null=True, blank=True)
    task = models.CharField(max_length=200)
    notes = models.CharField(max_length=300, blank=True)
    assigned_on = models.CharField(max_length=20, blank=True)
    assigned_by = models.CharField(max_length=50, blank=True)
    assigned_to = models.CharField(max_length=50, blank=True)
    due_date = models.CharField(max_length=20, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "worklists_task"
        ordering = ["-id"]


class StatusChange(models.Model):
    STATUS_CHOICES = [("Addition", "Addition"), ("Closure", "Closure")]

    client = models.ForeignKey(Client, related_name="status_change_set", on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Addition")
    start_date = models.CharField(max_length=20, blank=True)
    close_date = models.CharField(max_length=20, blank=True)
    notes = models.CharField(max_length=300, blank=True)
    payroll = models.BooleanField(default=False)
    payroll_cutoff = models.CharField(max_length=20, blank=True)
    sales_tax = models.BooleanField(default=False)
    sales_tax_cutoff = models.CharField(max_length=20, blank=True)
    taxes_other = models.BooleanField(default=False)
    taxes_other_cutoff = models.CharField(max_length=20, blank=True)
    added_by = models.CharField(max_length=50, blank=True)
    mod_date = models.CharField(max_length=20, blank=True)
    mod_by = models.CharField(max_length=50, blank=True)

    class Meta:
        managed = False
        db_table = "worklists_status_change"
        ordering = ["-id"]
