---
name: spendly-ui-designer
description: Generates modern, production-ready UI pages and components for Spendly, a Flask + Jinja2 personal expense tracker (github.com/campusx-official/spendly). Use this skill whenever the user asks to design, build, create, redesign, or improve any page or UI piece for Spendly — e.g. "design the dashboard page", "create UI for adding an expense", "build a component for the budget summary", "redesign the settings page", or any mention of Spendly's frontend, templates, or look-and-feel. Also trigger on general requests to build a clean fintech/SaaS-style HTML page or expense-tracker UI even if "Spendly" isn't named explicitly, if context suggests the same project. Outputs Jinja2 HTML templates and vanilla CSS (NOT React) — do not use this skill for unrelated Flask apps or non-UI backend work.
---

# Spendly UI Designer

Generates clean, modern, fintech-style UI for **Spendly**, a Flask + Jinja2 + vanilla CSS/JS personal
expense tracker. Spendly has no frontend framework — everything is server-rendered HTML templates
styled with plain CSS. Every output from this skill must match that stack. Never produce React,
Vue, JSX, or framework-specific component code here.

## Workflow

1. **Clarify the target.** Identify the page or component name (e.g. "dashboard", "add expense
   form", "budget card", "transactions table"). If the user's request is vague about what data or
   fields are involved, make a reasonable assumption based on typical expense-tracker needs (amount,
   category, date, note, account) and state the assumption briefly rather than stalling on questions.
2. **Check for reference material.** If the user has shared screenshots, an existing template, or a
   CSS file from their actual Spendly instance, treat that as the source of truth over the default
   design rules below — match its colors, spacing, and component patterns. If nothing is shared and
   nothing is available on disk, ask for a screenshot only if the request truly can't proceed without
   it (e.g. "match the existing style" with zero other context); otherwise proceed with the design
   rules below and mention that you're using the default Spendly style.
3. **Produce output in the four sections below, in order.** Don't skip sections; keep section 1 brief.
4. **Save real files**, not just inline code blocks, when the conversation is doing more than a quick
   sketch — a `.html` template and a `.css` file the user can drop into their project (see File
   Placement below).

## Output format

### 1. UI Structure (brief)
2-5 bullet points covering:
- Overall layout (e.g. sidebar + main content, single-column form, card grid)
- Key sections/regions and their purpose
- Notable UX decisions (e.g. "empty state shown when no transactions", "totals sticky at top on mobile")

Keep this short — it's a map of the page, not a essay.

### 2. Code
- One Jinja2 template file (`.html`) using `{% extends "base.html" %}` and a `{% block content %}`
  (or the equivalent block name already used in the project, if known) — never a full standalone
  `<html>` document unless explicitly asked for a standalone page.
- One CSS file (or a clearly-marked CSS block) with plain, modular class names (BEM-ish is fine:
  `.expense-card`, `.expense-card__amount`). No inline `style=` attributes except for truly
  one-off dynamic values (e.g. a progress-bar width set from a Jinja variable).
- Minimal vanilla JS only if the component needs interactivity (toggles, modals, live totals) —
  plain `<script>` tag or a small `.js` file, no build step, no frameworks.
- Use Jinja2 template syntax naturally for dynamic content: `{{ variable }}`, `{% for %}`, `{% if %}`.
  Assume the view passes in reasonably-named context variables and note what they'd need to be.

### 3. Design Quality
Confirm (briefly, as a checklist or short paragraph) how the output meets:
- Modern SaaS/fintech look — not generic Bootstrap-default or dated
- Card-based layout where appropriate, with soft shadows and rounded corners
- Clear visual hierarchy (size/weight/color contrast between primary and secondary info)
- Consistent spacing on an 8px grid (8, 16, 24, 32px etc.)
- Subtle, restrained color palette — avoid loud gradients or saturated fills; let one accent color do the work

### 4. Icons
- Use **Lucide** icons, since Spendly has no JS framework: pull inline SVGs from
  `https://unpkg.com/lucide-static@latest/icons/{icon-name}.svg`, or embed the raw SVG markup
  directly (preferred for production — no runtime fetch, no flash of missing icon).
- Never use `lucide-react` or any React icon package — Spendly can't consume it.
- Use icons purposefully: category icons, action buttons (add/edit/delete), empty states, nav items.
  Don't decorate for its own sake.

## Design Rules (default Spendly style)

Use these when no existing design reference is available:

- **Palette**: neutral base (off-white/very light gray background, dark slate text), one accent
  color for primary actions and positive amounts, a muted red/orange for expenses or negative
  amounts. Avoid more than 2-3 hues total.
- **Corners**: 8-12px border-radius on cards and inputs; 6-8px on buttons and chips.
- **Shadows**: soft and subtle — e.g. `box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);`.
  Never hard drop-shadows or heavy blur.
- **Spacing**: 8px grid throughout (padding, gaps, margins all multiples of 8, with 4px allowed for
  tight inline spacing like icon-to-label gaps).
- **Typography**: one clean system/sans-serif stack, 2-3 weights max (regular, medium, semibold).
  Numbers (amounts) can use tabular-nums for alignment in lists/tables.
- **Cards**: white/near-white surface on the neutral background, thin or no border, shadow for
  separation rather than heavy borders.

## Avoid

- Generic, dated, or "default Bootstrap" looking UI
- Unstructured code dumps with no explanation of layout or decisions
- Inline `<style>` soup instead of a real CSS file/block
- React, Vue, JSX, or any build-step-dependent code
- Overusing icons, gradients, or color — restraint is part of the fintech look
- Skipping the UI Structure section to jump straight to code

## File Placement

When saving real files (not just showing code inline), follow Spendly's existing conventions:
- Templates go under `templates/` (e.g. `templates/dashboard.html`)
- Styles go under `static/css/` (e.g. `static/css/dashboard.css`), linked via
  `<link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css') }}">`
- Any JS goes under `static/js/`, linked similarly with `url_for`

If the user is just exploring ideas or asked for a quick mockup, it's fine to show code inline
instead of writing files — use judgment based on how the request was phrased.