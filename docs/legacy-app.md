# The legacy Access application

`IASGMIS.accde` — deployed per user to `...\iasg\fe\<initials>\`, front-end
only, tables linked to MS SQL Server over ODBC.

**The source is not available.** `.accde` has VBA permanently stripped and
forms locked in design view. There is no decompiler. Unless an original
`.accdb` is found (see `open-questions.md`), **the running application is the
only specification.** Record what you observe; it is not recoverable later.

## Control Console — the main screen

Master client record with a tabbed detail area below.

**Header:** Client ID, entity type, active flag, name, DBA, two address lines,
city/state/zip, county, phone, email, federal ID + start date, state ID + sales
tax rate, withholding ID + SOS ID, unemployment ID + rate, bank name, routing
and account numbers, service flags (sales tax / payroll / taxes-other /
cigarette-tobacco-OTT), closed flag + date.

**Contacts grid:** name, email, receives-email, is-owner, phone, ownership %,
active. Plus a detail block with SSN, driver's licence, DOB.

**Record navigation:** first/prev/next/last, add, edit, save, delete, and a
name/phone search box.

## Tabs

| Tab | Columns | Write access |
|---|---|---|
| Notes | Category, Note, Date, Time, By, Mod_Date, Mod_Time, ModBy | add / edit / delete |
| Credentials | Site/Desc, Username, **Password**, Description/Notes, Active | add / edit / delete |
| Communications | Type, Content, Date, Time, By | none — generated |
| Sales Tax History | Year, Month, County, Due_Date, Submit_DT, Sales, Exempt, State_ST, COU_ST, City_ST, SPL_ST, SSTMOP | none — generated |
| Tasks | Client, Task, Notes, Assigned_On/By/To, Due_Date, Completed | add / edit / delete |
| Additions / Closures | Client, Status, Start_Dt, Close_Dt, Notes, Payroll, P_Cutoff_Dt, Sales_Tax, ST_Cutoff_Dt, Taxes, TO_Cutoff_Dt, Added_By, Mod_Dt, MOD_By | add / edit / delete |
| Bank Statements | Year, Month, Notes, Recd_Stored, Chk_Img_Recd, Date_Recd, Received_By, Data_Entered, Entered_By, DT_Completed | edit / delete |
| Annuals | Year, Client, Type, Due_Dt, Rqmt_Recd, Filed, Dt_Filed, Filed_By, Completed | edit / delete |
| Financial Statements | *(buttons, not a grid)* | — |
| Functions & Reports | *(buttons, not a grid)* | — |

**Filters present on tabs:** Tasks (Current Client / My Tasks / All Tasks);
Additions/Closures (All Clients / Corporations / Individuals); Bank Statements
(Current Year / Completed / All Years / Selected); Annuals (Current Year / All
Years / Completed / Pending).

**Three of these are firm-wide, not client-scoped** — Tasks,
Additions/Closures, and Annuals all have cross-client filters and a Client
column. In the new app they become standalone pages with their own URLs,
reachable without picking a client first.

**Four tabs have no add button** — their rows are produced by the batch
functions, not typed. Manual write surface is smaller than the tab count
suggests.

## Financial Statements tab

Date range picker, then: Import Bank Transactions, Manage Bank Transactions,
Profit & Loss Statement, Balance Sheet, Personal Financial Statement.

This is a bookkeeping module hiding behind five buttons — implies a
transaction store, a chart of accounts, categorisation, and period logic.
**Largest single piece of work in the project.**

## Functions & Reports tab

- **Financial:** Enter Monthly Sales Tax Data
- **Data generation:** Generate Bank Statement Log
- **Collaboration / exports:** Create Monthly Fees ACH Data File
- **Reporting:** Clients Missing Banking Info · Clients Missing Other Info ·
  Clients Services Listing
- **Weblinks:** Sales Tax Rates by Address

Six reports total across both tabs. Smaller than feared.

## Manage Sales Tax Data — batch screen

`MANAGE SALES TAX DATA FOR ALL CLIENTS`. All clients for one period in a wide
editable grid. Header: Year, Month, Re/Generate Data, client name filter, three
deadline tiers (1st/5th, 2nd/10th, 3rd/15th), filters (All / Incomplete /
Completed), A-Z and State filters, and counters — observed: Total 574,
Incomplete 16, Complete 558.

Columns: Lock, Client Name, Federal ID, State ID, County, "0" flag, Total
Sales, Exempt, Meal Tax, Source, ST Rate, State Amt, County Rt, County Amt,
City Rate, City Amt, SPCL Rt, Special Amt, MT Amt, TotalPayabl, Pay Mode,
Routing #, Bank Account #, Submit Date, Complete.

**Only Total Sales, Exempt and Meal Tax are typed.** Everything else is
computed from county rates or comes from the client record.

*Observation:* every cell showed `#Name?` — broken control sources on the
form in its current state.

## Client Addition Form

Single-column form: name, DBA, two address lines, city/state/zip, county,
corp type, phone, email, start date, service checkboxes, fees, federal ID,
state ID, SOS ID, withholding ID, unemployment ID + rate, data path, ST rate,
bank name, routing, account. Then **one** contact (the form says "You May Add
ONLY 1 Contact at this Time") with name, email, phone, SSN, DL, DOB,
receive-email, is-owner, percent owned. Then billing: category, notes, amount,
date, paid, and — enabled only when paid is ticked — paid date, MOP, payee
account.

Nothing is marked required and nothing is validated. **This is why "Clients
Missing Banking Info" and "Clients Missing Other Info" exist.** The new form
tracks completeness on the record instead of chasing it downstream.

## Other observations

- Application-level login (status bar shows the signed-in user), so a users
  table and some permission scheme exist server-side.
- Audit columns (`Mod_Date`, `Mod_Time`, `ModBy`, `By`) are used consistently.
- A per-client "Data Path" suggests a document folder per client.
