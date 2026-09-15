from django.db import models

from apps.clients.models import Client

# Prototype-only, managed=False (see apps/clients/models.py header — same
# LegacyRouter rule applies to this app label).


class SalesTaxEntry(models.Model):
    client = models.ForeignKey(Client, related_name="salestax_entries", on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()  # 1-12

    total_sales = models.CharField(max_length=20, default="0")
    exempt = models.CharField(max_length=20, default="0")
    meal_tax = models.CharField(max_length=20, default="0")
    pay_mode = models.CharField(max_length=10, blank=True)
    submit_date = models.CharField(max_length=20, blank=True)
    filed = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "salestax_entry"
        ordering = ["client__name"]
        constraints = [
            models.UniqueConstraint(fields=["client", "year", "month"], name="salestax_entry_unique_period"),
        ]
