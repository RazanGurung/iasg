# Security

The firm is a tax preparer, so the FTC Safeguards Rule and IRS Publication
4557 apply. Nothing here is a substitute for review by a qualified security
auditor before go-live.

## Current exposure (the baseline we are improving on)

- SSN, driver's licence, DOB, bank routing and account numbers stored without
  encryption and displayed in plain view
- **Client portal passwords shown in a grid column** on the Credentials tab —
  reversible or plaintext, visible to anyone who can open the app
- No field-level access control
- No record of who viewed what
- No HTTPS (Access speaks ODBC over the LAN)

Portal credentials are the most serious item: a leak there is account takeover
on clients' own tax and banking accounts, with the firm as custodian.

**Interim mitigation available today, before any rebuild:** restrict who can
open the Credentials tab.

## Requirements for the new system

### 1. Encryption at rest
SQL Server Always Encrypted, or application-level encryption via
`cryptography`. **Keys live outside the database.** A key stored beside the
ciphertext protects nothing.

Covers: SSN, DL, DOB, routing number, account number, portal passwords.

### 2. Credentials are a vault, not a table
Portal passwords must be reversible (we need to use them), so they can never
be hashed. Therefore:
- separate encryption key from other protected fields
- never rendered in a list or grid — one at a time, on explicit request
- every reveal logged: user, client, credential, timestamp
- if Playwright automation uses them, decrypt in memory and never display

### 3. Role-based access, enforced in views
Not everyone needs SSNs. Not everyone needs the ACH function. Hiding a button
in a template is not access control — the check goes in the view.

### 4. Audit logging
Extend the existing `Mod_*` convention to cover **reads** of protected fields,
not just writes. This is what turns a security claim into something
demonstrable to an auditor.

### 5. HTTPS on the LAN
Internal certificate. SSNs should not cross the office network in plaintext.

### 6. MFA
Required by the Safeguards Rule. Entra ID integration if staff are on the
domain, otherwise Django MFA.

## What the framework does not fix

- An unpatched server, an `sa` connection string, or unencrypted database
  backups on a share
- `raw()`, `.extra()`, and `|safe` — Django's escape hatches are still ours
  to misuse
- Anyone with SQL Server admin rights reads the tables directly regardless of
  application permissions

## Rules for this repo

- Fabricated data in every test, fixture, example, and screenshot
- Never log, print, or put a protected value in an error message
- No real client data in the repo, ever
