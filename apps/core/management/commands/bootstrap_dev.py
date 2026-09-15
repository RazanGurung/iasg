"""
Prototype-only dev bootstrap.

Creates the local SQLite tables for the "legacy" apps (clients, salestax,
worklists) directly with the schema editor — NOT via `makemigrations`/
`migrate`, which config/routers.py's LegacyRouter permanently refuses for
those app labels (Access is still using the real tables; nothing here may
ever generate migration DDL against them). This command is the one place
allowed to create those tables locally, once, for prototype development.

Safe to re-run: every step is idempotent (checks before creating/seeding).
"""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import connection

from apps.clients.models import AnnualLiability, BankStatement, Client, Contact, Credential, Note
from apps.salestax.models import SalesTaxEntry
from apps.worklists.models import StatusChange, Task

# (name, county, state, state_rate, county_rate, city_rate, special_rate, mode, filed)
_ROSTER = [
    ("ASHWORTH LANE MARKET LLC", "Guilford", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", True),
    ("BRIAR CREEK FUEL STOP INC", "Forsyth", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", True),
    ("CEDAR POINT GROCERY LLC", "Halifax", "VA", "0.043", "0.01", "0.000", "0.007", "Check", True),
    ("DELMAR TOBACCO OUTLET", "Guilford", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", False),
    ("EASTGATE CONVENIENCE INC", "Wake", "NC", "0.0475", "0.02", "0.005", "0.000", "ACH", True),
    ("FAIRVIEW MARKET & DELI", "Forsyth", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", False),
    ("GLENWOOD SUPPLY CO", "Durham", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", True),
    ("HARPERS MILL DISCOUNT", "Halifax", "VA", "0.043", "0.01", "0.000", "0.007", "Check", False),
    ("IRONWOOD SERVICE CENTER", "Guilford", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", False),
    ("JUNIPER STREET CAFE", "Wake", "NC", "0.0475", "0.02", "0.005", "0.000", "ACH", False),
    ("KESTREL FOOD MART LLC", "Forsyth", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", False),
    ("LAUREL RIDGE PANTRY", "Durham", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", False),
    ("MAPLE HOLLOW STORE INC", "Guilford", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", False),
    ("NORTHFIELD TRADING CO", "Halifax", "VA", "0.043", "0.01", "0.000", "0.007", "Check", False),
    ("OAKLINE BEVERAGE LLC", "Wake", "NC", "0.0475", "0.02", "0.005", "0.000", "ACH", False),
    ("PINEHURST QUICK STOP", "Forsyth", "NC", "0.0475", "0.0225", "0.005", "0.000", "ACH", False),
]

_MODELS = [Client, Contact, Note, Credential, BankStatement, AnnualLiability, SalesTaxEntry, Task, StatusChange]


class Command(BaseCommand):
    help = "Create local prototype tables and seed fabricated demo data (dev only)."

    def handle(self, *args, **options):
        self._create_tables()
        self._seed_users()
        self._seed_clients()
        self.stdout.write(self.style.SUCCESS("bootstrap_dev complete."))

    def _create_tables(self):
        existing = set(connection.introspection.table_names())
        with connection.schema_editor() as editor:
            for model in _MODELS:
                if model._meta.db_table not in existing:
                    editor.create_model(model)
                    self.stdout.write(f"created table {model._meta.db_table}")

    def _seed_users(self):
        User = get_user_model()
        for username, password, is_super in [
            ("rgurung", "prototype123", True),
            ("adixit", "prototype123", False),
        ]:
            if not User.objects.filter(username=username).exists():
                if is_super:
                    User.objects.create_superuser(username, password=password)
                else:
                    User.objects.create_user(username, password=password)
                self.stdout.write(f"created login user {username}")

    def _seed_clients(self):
        if Client.objects.exists():
            self.stdout.write("clients already seeded, skipping")
            return

        ashgrove = Client.objects.create(
            type="S-Corp", name="ASHGROVE FUEL & VARIETY INC", dba="",
            address1="4410 PINEVALE RD STE 6", address2="",
            city="BURLINGTON", state="NC", zip="27215", county="ALAMANCE",
            phone="(336) 555-0148", email="ap@ashgrovefuel.example",
            federal_id="58-1120044", start_date="14 Sep 2021",
            state_id="20-581120044F-001", st_rate="0.0700",
            withholding_sos_id="40-581120044F-001", sos_id_value="10228815",
            unmp_id="0038871200", unmp_rate="0.0110",
            bank_name="Carolina Trust Bank", routing_number="053100300", account_number="4471200512",
            state_rate="0.0475", county_rate="0.0225", city_rate="0.005", special_rate="0.000",
            sales_tax=True, payroll=True, taxes_other=False, cig_tob=True,
        )
        Contact.objects.create(
            client=ashgrove, name="DIANE M. OKAFOR", email="diane.okafor@ashgrovefuel.example",
            phone="(336) 555-0148", receives_email=True, is_owner=True, pct="60",
            ssn="000-00-6031", drivers_license="D1234567", dob="12 Mar 1978",
        )
        Contact.objects.create(
            client=ashgrove, name="LARRY T. FENWICK", email="lfenwick@ashgrovefuel.example",
            phone="(336) 555-0172", receives_email=False, is_owner=False, pct="40",
        )
        Note.objects.create(
            client=ashgrove, category="General", text="Ownership updated, Okafor confirmed at 60%",
            date="14 Aug 2026", time="10:12 AM", by="rgurung",
            mod_date="14 Aug 2026", mod_time="10:40 AM", mod_by="rgurung",
        )
        Note.objects.create(
            client=ashgrove, category="Sales tax", text="Moved to online filing, credentials updated",
            date="02 Jul 2026", time="09:05 AM", by="adixit",
        )
        Credential.objects.create(
            client=ashgrove, site="Online Sales & Use Tax Portal", username="ashgrove.filer",
            password="proto-demo-1", notes="State DOR portal login", active=True,
        )
        Credential.objects.create(
            client=ashgrove, site="NC Secretary of State", username="ashgrove_admin",
            password="proto-demo-2", notes="Annual report filing", active=True,
        )
        BankStatement.objects.create(
            client=ashgrove, year=2026, month="Aug", received_stored=True, check_image_received=True,
            date_received="03 Sep 2026", received_by="rgurung", data_entered=True,
            entered_by="adixit", date_completed="05 Sep 2026",
        )
        AnnualLiability.objects.create(
            client=ashgrove, year=2026, type="Annual report", due_date="15 Apr 2026",
            requirement_received=True, filed=True, date_filed="02 Apr 2026",
            filed_by="rgurung", completed=True,
        )

        riverton = Client.objects.create(
            type="S-Corp", name="RIVERTON HARDWARE & SUPPLY LLC", dba="Riverton Supply",
            address1="4180 Chestnut Ridge Rd, Ste 120", address2="",
            city="GREENSBORO", state="NC", zip="27405", county="GUILFORD",
            phone="(336) 555-0182", email="ap@rivertonsupply.example",
            federal_id="55-4180992", start_date="02 Feb 2019",
            state_id="60-554180992-001", st_rate="0.0675",
            withholding_sos_id="30-554180992-001", sos_id_value="0041872300",
            unmp_id="0041872300", unmp_rate="0.0120",
            bank_name="Piedmont Federal", routing_number="053112345", account_number="88126789",
            state_rate="0.0475", county_rate="0.0225", city_rate="0.005", special_rate="0.000",
            sales_tax=True, payroll=True, taxes_other=False, cig_tob=False,
        )
        Contact.objects.create(
            client=riverton, name="DALE W. RIVERTON", email="dale@rivertonsupply.example",
            phone="(336) 555-0182", receives_email=True, is_owner=True, pct="60",
            ssn="000-00-8127", drivers_license="D7654321", dob="04 Nov 1971",
        )
        Contact.objects.create(
            client=riverton, name="MARIA OKONKWO", email="maria@rivertonsupply.example",
            phone="(336) 555-0193", receives_email=True, is_owner=True, pct="40",
        )
        Note.objects.create(
            client=riverton, category="General",
            text="Ownership change filed with SOS, Okonkwo added at 40%",
            date="14 Aug 2026", time="09:41 AM", by="rgurung",
            mod_date="14 Aug 2026", mod_time="09:52 AM", mod_by="rgurung",
        )

        rich = {ashgrove.name, riverton.name}
        for i, (name, county, state, st, co, ci, sp, mode, filed) in enumerate(_ROSTER):
            client = Client.objects.create(
                type="S-Corp", name=name, city=county.upper(), state=state, county=county,
                phone=f"(336) 555-0{200 + i:03d}",
                email=f"ap@{name.split()[0].lower()}.example",
                federal_id=f"{100000000 + (i * 8111071) % 900000000:09d}",
                state_id=f"{100000000 + (i * 9130057) % 900000000:09d}",
                bank_name="First National Bank",
                routing_number=f"05140{3000 + i}", account_number=f"{4172800 + i}",
                state_rate=st, county_rate=co, city_rate=ci, special_rate=sp,
                sales_tax=True, payroll=False, taxes_other=False, cig_tob=False,
            )
            Contact.objects.create(client=client, name=f"{name.split()[0].title()} Owner",
                                    email=client.email, phone=client.phone, is_owner=True, pct="100")
            SalesTaxEntry.objects.create(
                client=client, year=2026, month=8, pay_mode=mode if filed else "", filed=filed,
                total_sales="0" if not filed else "0", exempt="0", meal_tax="0",
                submit_date="5 Sep 2026" if filed else "",
            )

        for client_name, sales, exempt in [
            ("ASHWORTH LANE MARKET LLC", "318402.55", "12440.10"),
            ("BRIAR CREEK FUEL STOP INC", "204118.90", "8802.44"),
            ("CEDAR POINT GROCERY LLC", "167230.18", "5410.77"),
            ("EASTGATE CONVENIENCE INC", "441908.33", "18220.91"),
            ("GLENWOOD SUPPLY CO", "276014.77", "9911.30"),
        ]:
            SalesTaxEntry.objects.filter(client__name=client_name, year=2026, month=8).update(
                total_sales=sales, exempt=exempt,
            )

        Task.objects.create(
            client=ashgrove, task="Prepare Q3 sales tax filing", notes="Awaiting bank statement",
            assigned_on="01 Sep 2026", assigned_by="rgurung", assigned_to="adixit",
            due_date="15 Sep 2026", completed=False,
        )
        Task.objects.create(
            client=ashgrove, task="Confirm new contact ownership %",
            assigned_on="28 Aug 2026", assigned_by="rgurung", assigned_to="rgurung",
            due_date="05 Sep 2026", completed=True,
        )
        self.stdout.write(f"seeded {Client.objects.count()} clients")
