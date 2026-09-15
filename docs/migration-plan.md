# Migration plan

**Goal: no cutover.** Both systems run against the same database, behaving
identically, until Access is empty. Any module can fall back independently.

## Three conditions this depends on

**1. The database is the source of truth, not the front-end.**
Shared rules live in SQL Server as stored procedures, views, constraints and
triggers. Access calls them through pass-through queries; the new app calls
the same ones. One implementation, two callers. Otherwise the systems drift
the moment both are live.

**2. Exactly one system sends client email.**
If both can send, clients get duplicates — a client-facing failure at an
accounting firm. Move sending to SQL Server Agent / Database Mail or a
scheduled job, with a sent-log table and a uniqueness constraint that makes
double-sending impossible. The Communications tab is already this log.

**3. Concurrency is handled explicitly.**
Access uses record locking on bound forms; a web app cannot. Add `rowversion`
to every shared table, read it with the record, check it on save, reject on
change. Without this, a save from one system silently overwrites the other.

## Order

1. **Inventory** — record every screen from the running app (source is
   unavailable). Screenshots plus field notes.
2. **Email moves out** to a scheduled job with a sent-log. Access unchanged.
3. **Logic moves into SQL Server**, procedure by procedure. Access rewired to
   call them. Users notice nothing.
4. **`rowversion` added**, both sides checking it.
5. **New app, read-only** — search, console, all tabs. No write risk, and it
   covers the majority of actual usage. Ship to two users.
6. **Writes, one tab at a time.** Notes first (low stakes, high volume). Each
   Access screen is disabled only after its replacement has run for a couple
   of weeks.
7. **Access shrinks** to a shell, then goes.

Steps 2–4 are worth doing even if the rebuild never happens.

## Fixes vs port

Improvements go into **SQL Server**, where both systems see them the same day.
The new front-end **ports faithfully and changes nothing**, so that "same
input, same result" stays a valid test during parallel running. UI-level
improvements go on a list and ship after Access is retired.

## Effort notes

- CRUD is lighter than the ten tabs suggest — four tabs accept typed input
- Six reports, three of them simple exception lists
- Financial statements module is the heavy item — build it last
- ACH generation is small but the highest-risk deliverable
- Without the Access source, add roughly 30–50% to any estimate
