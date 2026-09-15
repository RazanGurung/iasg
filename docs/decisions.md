# Decisions

Recorded so nobody relitigates these without new information.

## 1. Replace the front-end, not the database

The data is already in MS SQL Server. Access is only the UI. The database
stays exactly as it is; this project builds a new front-end against it.

## 2. Access is not end-of-life — this is planned work, not a fire

Microsoft still ships Access in Microsoft 365 and Access LTSC 2024, with no
published end date. It is in maintenance mode: Access Web Apps died in 2017,
Database Compare retires June 2026, and Microsoft's low-code direction is
Power Platform. So there is a planning window, which is what makes incremental
migration possible.

**The real drivers are not "Access is old":**

- The `.accde` is compiled. Nobody can modify it. The developer has left.
- No source, no documentation, no version control.
- SSNs, bank details, and client portal passwords stored and displayed without
  encryption, access control, or audit logging.
- Windows Server 2022 support for M365 Apps ends October 2026.

Point 3 is the one that justifies the budget.

## 3. Rejected: Power Apps

The SQL Server connector is a premium connector, so every user needs a Power
Apps Premium licence on top of their existing M365 seat. US list rose to
$22/user/month (annual) on 1 September 2026. At 25 users that is ~$6,600/year,
~$33,000 over five years, forever, owning nothing.

The current Access front-end costs $0 — Access is bundled in M365 Business
Standard, Business Premium, and E3/E5, and the Access Runtime is free for
users who only run the app. Power Apps roughly doubles the per-user Microsoft
spend to replace something already included.

Rejected on cost. Nothing technical about it was wrong.

## 4. Rejected: third-party low-code (Budibase, Appsmith, Retool)

Viable and fast, but the firm wants to own the software outright. Excluded by
requirement, not by capability.

## 5. Rejected: React + API

Would mean two codebases, a Node toolchain, and a separate solution for PDF
reports. The mockups settled it empirically: the most interactive screen — the
sales tax batch grid with live tax computation and running totals — needed
about 80 lines of vanilla JS. The interactivity is localised, not pervasive.

*Reversal note:* an earlier argument for React was dirty-state tracking across
a large tabbed form. The read-first design (explicit edit mode) removed almost
all client-side state, so the argument no longer holds.

## 6. Rejected: .NET / Blazor

Technically a strong fit for SQL Server. Rejected because the team's language
is Python, and one maintainer is the constraint that matters here.

## 7. Chosen: Django + HTMX + Alpine, server-rendered

- `inspectdb` generates models from the existing schema — no modelling phase
- Auth, sessions, permissions, CSRF, and validation come with the framework
- Ten similar tab modules suit generic views; build one well, configure nine
- WeasyPrint renders reports from the same HTML/CSS as the UI
- ACH generation, the P&L engine, and Playwright automation are all plain Python
- One language, one repo, no build pipeline

## 8. Delivery: server-hosted, thin desktop shell

Django runs as a Windows service on the existing server; SQL Server is on the
same box, so the DB connection is local (shared memory / named pipes) — the
fastest path available, and no ODBC-over-network encryption problem.

Users currently get a per-user server instance. A browser-delivered app can
skip that entirely, freeing 1–2 GB of session RAM per user.

**Order of attempts for the desktop feel:**

1. **Edge app mode** (`msedge.exe --app=http://server:PORT/`) — chromeless
   window, signed Microsoft binary, nothing to package, nothing to sign,
   nothing for antivirus to quarantine. Start here.
2. **pywebview + PyInstaller** if native file dialogs, local printing, or
   filesystem access turn out to matter. Uses the WebView2 runtime already in
   Windows (~20–40 MB), driven from Python.

**Rejected: Electron.** Ships its own Chromium (150–250 MB, ~250–400 MB RAM
per instance). With per-user server instances that is a capacity problem on
the box running SQL Server. It would also add a Node toolchain to a repo that
deliberately has none.

**If PyInstaller is used:** build `--onedir`, not `--onefile` (temp-directory
unpacking is a primary antivirus heuristic), get the exe code-signed, and have
admins add a Defender exclusion by Group Policy. Check with VirusTotal before
rollout.

## 9. Browser automation runs server-side, in its own process

Playwright (preferred over Selenium — better waiting, browser contexts per
client, download interception). Never inside a user's app window: automation
must survive the window closing, must not run twice concurrently against one
portal account, and must not put credentials on workstations.

Check each portal's terms and MFA posture before automating it.
