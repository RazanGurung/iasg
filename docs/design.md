# Design

Approved mockups are in `docs/mockups/`. Open the relevant one before building
a screen — they are the spec, not inspiration. Shared CSS lives in
`static/css/app.css`; shared markup lives in `templates/partials/`. Both are
generated from the tokens and components below — see
`docs/mockups/component-preview.html` for every component on one page.

## Source of truth

The legacy Access screens (`public/*.webp`, not committed — see
`docs/security.md`) are the visual reference. Colors and chrome below were
**sampled directly from those screenshots**, not eyeballed:

- Window frame: a thin (~1px) muted brick-maroon border, `#7a4f50`, wraps the
  whole console.
- Content surfaces (fields, grids, panels) are white, `#ffffff` — not grey.
- The tab strip is a flat light-grey band, `#d9d9d9`. Inactive tabs are plain
  black text sitting directly on that band — there is no per-tab box. The
  active tab is a white cut-out.
- A selected grid/list row is a near-black highlight (`#1a1a1a` bg, white
  text) — not the usual Windows selection blue.
- Grid headers are white with black text and a thin grey rule underneath —
  no shaded header band.
- The one added accent color is a muted blue (`#2c5aa0`), used sparingly for
  focus rings and the reveal affordance on protected values. Everything else
  is black-on-white-on-grey.

**Deviations from the legacy look, and why:**

- **Row height and type scale are bumped up.** The legacy grid runs
  ~16–18px rows at ~11px type — measured directly off the Notes grid. That is
  too tight to be an improvement on a 1920x1080 screen with 1.5x the area of
  the original ~1500x840 layout. Bumped to 24px rows / 12.5px type: still
  visibly denser than a typical modern app, but no longer eye-straining.
- **Protected values (SSN, DL, DOB, routing/account, portal passwords) are
  masked by default, revealed one at a time, every reveal logged.** The
  legacy app shows these in the clear in a grid. This is a security
  requirement (`docs/security.md`), not a style choice, and it overrides
  visual fidelity here specifically.
- **Dates render as `14 Aug 2026`**, not the legacy `2/2/2022`. Unambiguous
  and faster to read; a formatting choice, not a chrome choice.

Everything else — boxed fields, the flat grey tab band, the maroon frame,
the black-on-white palette, the black row-selection highlight — is ported
faithfully.

## Target

1920x1080, maximised. Roughly 980px of usable viewport height. The legacy
Access form was built at ~1500x840 and never reflowed, so there is ~1.5x the
area available. That headroom goes into readable density (bigger rows,
bigger type), not decoration — the chrome itself stays plain.

## Three archetypes

**1. Record console** (`client-console-v2.html`) — one client, tabbed detail.
Fields render as boxed, readonly-looking inputs (white, thin grey border) —
matching the legacy field boxes. An explicit "Edit client" mode swaps them to
live, focusable inputs with an accent-colored focus rule. Escape or Cancel
exits. *(This mockup currently still uses the old read-first/underlined
style from before the Access-matched direction was adopted — it needs a pass
to catch up with the tokens below.)*

**2. Batch worklist** (`sales-tax-batch.html`) — many clients, one period,
wide grid. Frozen client column, grouped column headers, computed cells
shaded and skipped by Tab, rate columns hidden behind a toggle, pinned totals
row, default filter is the rows needing work rather than all rows.

**3. Creation form** (`new-client-form.html`) — three columns plus a
completeness sidebar. Real validation (ABA checksum on routing numbers, EIN
format), duplicate-name check, multiple contacts, conditional billing fields.

## Rules

- **No UI framework.** Component kits assume touch targets and mobile-first
  spacing; they would cost information density for no reason here. Own CSS
  in `static/css/app.css`, shared across every screen.
- **Base font 12.5px, row/field height 24px.** Legacy is ~11px / ~16-18px
  rows — this is the minimum bump that stays crisp on a 1920x1080 screen
  without drifting airy. Don't go bigger than this without a reason.
- **CSS Grid** for label/value alignment. Access forms are coordinate-based;
  Grid is how you match that without absolute positioning.
- **Tabular numerals** on every numeric field so digits align vertically.
- **Distinguish entered from computed.** Computed cells get a grey
  background, no input border, and are skipped in the tab order.
- **Protected values masked by default**, click or Enter to reveal, logged.
- **Density over whitespace.** Internal tools should be plain, high-contrast,
  and information-dense. Boring is a feature — this was already true of the
  legacy app, and it's still true now that the chrome matches it.
- **Dates as `14 Aug 2026`**, not `08/14/2026` or `2/2/2022` — unambiguous
  and faster to read.

## Keyboard

Users are fast Access typists. Access gave them tab order, Enter-to-commit,
and focus placement for free; on the web every one of those is written.

- Focus lands in the first meaningful field on load
- Explicit tab order matching visual reading order
- Enter commits and advances (in the batch grid, to the next open row)
- Escape cancels an edit
- `/` focuses search; arrow keys move between tabs
- Unsaved changes warn before navigation

Ask the two heaviest users which shortcuts they currently press. There will be
some nobody has written down.
