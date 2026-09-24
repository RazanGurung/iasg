from django.db import models

# Prototype-only models for local development. These mirror the eventual
# legacy-table shape closely enough to demo real CRUD, but managed=False and
# config/routers.py's LegacyRouter permanently block `makemigrations`/`migrate`
# for this app label — the tables are created directly with SQL by
# apps.core.management.commands.bootstrap_dev instead. See CLAUDE.md: legacy
# tables are never Django-migrated, Access is still using them.


class Client(models.Model):
    type = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=200)
    dba = models.CharField(max_length=200, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=10, blank=True)
    zip = models.CharField(max_length=15, blank=True)
    county = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.CharField(max_length=200, blank=True)

    federal_id = models.CharField(max_length=30, blank=True)
    start_date = models.CharField(max_length=20, blank=True)
    state_id = models.CharField(max_length=30, blank=True)
    st_rate = models.CharField(max_length=20, blank=True)
    withholding_sos_id = models.CharField(max_length=30, blank=True)
    sos_id_value = models.CharField(max_length=30, blank=True)
    unmp_id = models.CharField(max_length=30, blank=True)
    unmp_rate = models.CharField(max_length=20, blank=True)

    bank_name = models.CharField(max_length=200, blank=True)
    routing_number = models.CharField(max_length=30, blank=True)
    account_number = models.CharField(max_length=30, blank=True)

    # The firm's own monthly service fee, debited via apps.ach — distinct
    # from sales tax remitted on the client's behalf. legacy-app.md's Client
    # Addition Form has a "fees" field on the same single-column form; no
    # separate Billing model exists yet (see that doc's "billing: category,
    # notes, amount..." section), so this is a flat per-client amount for now.
    monthly_fee = models.CharField(max_length=10, default="0", blank=True)

    # Sales-tax jurisdiction rates used by apps.salestax when computing a
    # period's amounts for this client.
    state_rate = models.CharField(max_length=10, default="0")
    county_rate = models.CharField(max_length=10, default="0")
    city_rate = models.CharField(max_length=10, default="0")
    special_rate = models.CharField(max_length=10, default="0")

    sales_tax = models.BooleanField(default=False)
    payroll = models.BooleanField(default=False)
    taxes_other = models.BooleanField(default=False)
    cig_tob = models.BooleanField(default=False)

    active = models.BooleanField(default=True)
    closed = models.BooleanField(default=False)
    date_closed = models.CharField(max_length=20, blank=True)

    class Meta:
        managed = False
        db_table = "clients_client"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(models.Model):
    client = models.ForeignKey(Client, related_name="contact_set", on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    receives_email = models.BooleanField(default=True)
    is_owner = models.BooleanField(default=False)
    pct = models.CharField(max_length=10, blank=True)
    ssn = models.CharField(max_length=20, blank=True)
    drivers_license = models.CharField(max_length=30, blank=True)
    dob = models.CharField(max_length=20, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "clients_contact"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Note(models.Model):
    client = models.ForeignKey(Client, related_name="note_set", on_delete=models.CASCADE)
    category = models.CharField(max_length=50, blank=True)
    text = models.TextField()
    date = models.CharField(max_length=20, blank=True)
    time = models.CharField(max_length=20, blank=True)
    by = models.CharField(max_length=50, blank=True)
    mod_date = models.CharField(max_length=20, blank=True)
    mod_time = models.CharField(max_length=20, blank=True)
    mod_by = models.CharField(max_length=50, blank=True)

    class Meta:
        managed = False
        db_table = "clients_note"
        ordering = ["-id"]


class Credential(models.Model):
    client = models.ForeignKey(Client, related_name="credential_set", on_delete=models.CASCADE)
    site = models.CharField(max_length=200)
    username = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=200, blank=True)
    notes = models.CharField(max_length=300, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "clients_credential"
        ordering = ["id"]


class BankStatement(models.Model):
    client = models.ForeignKey(Client, related_name="bank_statement_set", on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.CharField(max_length=10)
    notes = models.CharField(max_length=300, blank=True)
    received_stored = models.BooleanField(default=False)
    check_image_received = models.BooleanField(default=False)
    date_received = models.CharField(max_length=20, blank=True)
    received_by = models.CharField(max_length=50, blank=True)
    data_entered = models.BooleanField(default=False)
    entered_by = models.CharField(max_length=50, blank=True)
    date_completed = models.CharField(max_length=20, blank=True)

    class Meta:
        managed = False
        db_table = "clients_bank_statement"
        ordering = ["-year", "-id"]


class AnnualLiability(models.Model):
    client = models.ForeignKey(Client, related_name="annual_set", on_delete=models.CASCADE)
    year = models.IntegerField()
    type = models.CharField(max_length=100, blank=True)
    due_date = models.CharField(max_length=20, blank=True)
    requirement_received = models.BooleanField(default=False)
    filed = models.BooleanField(default=False)
    date_filed = models.CharField(max_length=20, blank=True)
    filed_by = models.CharField(max_length=50, blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "clients_annual_liability"
        ordering = ["-year", "-id"]
