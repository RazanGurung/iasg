# Open questions

Check here before assuming anything about the domain. Answer them in place as
they are resolved.

## Blocking

- [ ] **Does an uncompiled `.accdb` exist anywhere?** The deployed file is
      `.accde` with VBA stripped. Search: the `iasg` share and its parents,
      backups from several years ago, the departed developer's profile or
      workstation image, old server images. Also find the logon script or GPO
      that copies the front-end into `fe\<user>` — it names the master path.
      *Finding this saves months.*
- [ ] **Are Credentials passwords stored recoverably?** (They display in a
      grid, so almost certainly yes.) Determines the vault migration path.
- [ ] **What format does Import Bank Transactions accept** — bank CSV, OFX/QFX,
      or something clients email in?
- [ ] **Current ACH file format** — get a real sample, redacted.

## Infrastructure

- [ ] Windows Server version on the session host. **M365 Apps support on
      Server 2022 ends October 2026**; 2019 and 2016 already ended.
- [ ] Can a Python runtime be installed and a Windows service registered on
      that server, or is it change-controlled?
- [ ] Is WebView2 present (only matters if pywebview is used)?
- [ ] Can anything be installed on workstations at all? If locked down, Edge
      app mode is the only delivery option.
- [ ] Which M365 plan are staff on? Shared Computer Activation is required to
      run Office on a session host, and Business Standard does not include it.
- [ ] Are RDS CALs in place? Licensed separately from M365.

## Domain

- [ ] How is Sales Tax Rates by Address used — manual lookup, or does
      something import rates?
- [ ] What computes State/County/City/Special splits today, and where do the
      rates come from?
- [ ] Is the per-client "Data Path" typed by hand or derived from client ID?
- [ ] Which of the six reports does anyone actually run? Retiring dead ones is
      the largest available effort saving.
- [ ] Which tabs are genuinely in use? (User: "some are not complete, some are
      not used, not feasible.") Confirm before rebuilding any of them.
- [ ] Do users rely on sequential record navigation (first/prev/next/last), or
      is search sufficient?
- [ ] Which portals would be automated, and do their terms and MFA allow it?
- [ ] How many concurrent users, and what does the Tasks worklist look like
      across the whole firm?
