# IASG MIS

Django replacement for the legacy MS Access client management application.
The MS SQL Server database is unchanged and shared with Access during
migration.

**Read `CLAUDE.md` first** — it holds the constraints. Detail is in `docs/`.

## Setup

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env        # fill in DB settings
    python manage.py check

## Generating models from the existing schema

Run against a **restored copy**, never production:

    python manage.py inspectdb --database=legacy > apps/clients/models_generated.py

Then split by app and set `managed = False` on every model. See
`scripts/inspect_legacy.py`.

## Running

    python manage.py runserver          # development
    python launcher.py                  # native window (pywebview)

Production: Waitress as a Windows service behind IIS. See `docs/decisions.md`.

## Rules that will bite you

- Never `makemigrations` against legacy tables — `managed = False` everywhere
- No Node, no npm, no bundler in this repo
- No real client data in tests, fixtures, or screenshots
