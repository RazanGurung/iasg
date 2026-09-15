"""Generate Django models from the existing SQL Server schema.

Run against a RESTORED COPY, never production.

    python scripts/inspect_legacy.py > apps/clients/models_generated.py

Then split the output by app and confirm every class has managed = False.
inspectdb sets it already; the check exists because losing it once would let
makemigrations propose DDL against tables Access is still using.
"""
import os
import sys

import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

call_command("inspectdb", database="legacy", stdout=sys.stdout)
