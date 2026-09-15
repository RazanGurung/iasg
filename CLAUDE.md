# IASG MIS — replacement for the legacy Access application

Client management system for an accounting firm (~1,850 clients, ~574 filing
monthly sales tax). Replaces `IASGMIS.accde`, an MS Access front-end over an
existing MS SQL Server database.

## Non-negotiables

- **The database already exists and is not ours to change.** Every model
  mirroring a legacy table MUST have `managed = False`. Never run
  `makemigrations` against legacy tables. Django's own tables (auth, sessions,
  audit) live in a separate schema.
- **Single package.** Server-rendered Django. No REST API layer, no JSON
  contract, no separate front-end build. Views return HTML; HTMX swaps HTML
  fragments. No Node, no npm, no bundler in this repo.
- **No UI framework.** Hand-written CSS in `static/css/`. Bootstrap, Tailwind,
  Material and friends are explicitly rejected — see `docs/design.md`.
- **Access stays live during the whole build.** Both systems run against the
  same database. Anything that changes behaviour goes into SQL Server so both
  callers get it. The new front-end ports faithfully and changes nothing.
- **Exactly one system sends client email.** See `docs/migration-plan.md`.

## Stack

Python 3.12 · Django 5.x · `mssql-django` + ODBC Driver 18 · HTMX · Alpine.js ·
WeasyPrint (reports) · Playwright (portal automation) · Waitress behind IIS on
the existing Windows server. SQL Server is local to that box.

## Layout

- `apps/clients/` — client console, new-client form, notes, contacts, credentials
- `apps/salestax/` — monthly batch grid, liability history
- `apps/banking/` — bank statements, transaction import
- `apps/financials/` — P&L, balance sheet (largest unknown; build last)
- `apps/worklists/` — tasks, additions/closures (firm-wide, NOT client-scoped)
- `apps/comms/` — communications log, the automated monthly client email
- `apps/ach/` — monthly fees ACH file (highest risk; see `docs/ach.md`)
- `apps/reports/` — six reports via WeasyPrint
- `apps/security/` — field encryption, credential vault, audit log
- `apps/core/` — base templates, auth, permissions, shared helpers

## Sensitive data — read `docs/security.md` before touching these

Legacy tables hold SSN, driver's licence, DOB, bank routing/account numbers,
and **client portal passwords in recoverable form**. Rules:

- Never render a protected value in a list or grid. Masked by default,
  revealed one at a time on explicit action, and every reveal is logged.
- Encryption keys live outside the database. Always.
- Never log, print, or include a protected value in an error message,
  fixture, test, or commit.
- Use fabricated data in every example, test, and screenshot.

## Conventions

- Read-first UI: values render as text; editing is an explicit mode.
- Distinguish entered fields from computed ones visually (see the mockups).
- Money: `Decimal`, never float. Tax amounts round per jurisdiction rules.
- Every legacy table has audit columns (`Mod_Date`, `ModBy`) — keep writing them.
- Concurrency: check `rowversion` on save. Access is editing the same rows.
- Keyboard matters. Users are fast typists coming from Access forms.

## Where the detail lives

| File | Contents |
|---|---|
| `docs/decisions.md` | Why this stack, alternatives rejected and why |
| `docs/legacy-app.md` | The Access app: tabs, fields, what each screen does |
| `docs/design.md` | Layout rules, density, the three UI archetypes |
| `docs/security.md` | Encryption, credentials, access control, compliance |
| `docs/migration-plan.md` | Build order, parallel running, cutover |
| `docs/open-questions.md` | What nobody knows yet — check before assuming |
| `docs/mockups/` | Approved HTML mockups. Open them before building a screen. |

## When working here

- The mockups in `docs/mockups/` are the design spec. Match them.
- If a legacy behaviour is unclear, **ask** — do not invent it. The Access
  source is unavailable (`.accde`, VBA stripped), so guesses become permanent.
- Check `docs/open-questions.md` before making an assumption about the domain.
