---
name: ui-development
description: Process for building, modifying, or fixing any user interface - web pages, web apps, and native GUIs (Tauri, egui, Slint, iced, Tkinter, Qt) in any language. Orchestrates the ready-made UI skills (frontend-design for taste, ui-ux-pro-max for style references, webapp-testing for verification, interface-design for decision memory, web-design-guidelines for the pre-ship audit) on top of the four-stage process: compose from existing parts, layout before style, deliberate style, verify in the running app. Use for ANY UI task, even small ones - adding a button, fixing a layout, styling a form, building a screen, or "the app looks broken".
---

# UI Development

**Core idea:** two things break agent-driven UI work. First, writing markup that looks plausible in code but falls apart when rendered. Second, *inventing* taste from training-data defaults — Inter font, purple gradients, three cards with emojis. The fix is the same for both: never work blind. Route aesthetic judgment to the dedicated skills already installed, follow a fixed process, and verify everything in the running app.

This skill is the **coordinator**. It does not contain better taste than the skills below — it dispatches to them, keeps the process coherent, and covers what they don't: native desktop GUIs, quality states, and the verification loop.

## Ready skills before custom rules

Before doing UI work yourself, check whether an installed skill owns the decision. This is not optional politeness — installed skills carry curated rules and databases this skill deliberately does not duplicate, and having several of them give *different* font or palette advice produces a confused mix. So there is exactly one owner per concern:

| Concern | Owner | When |
|---|---|---|
| Aesthetic direction, typography, layout character (web) | `frontend-design` | Before styling any web UI — read it at stage 3, always. |
| Style/palette/font UX databases, per-stack reasoning | `ui-ux-pro-max` | When the project has no design system yet, or the user asks for one built ("fintech app", "meditation app") — consult it *once* for a researched design system, then build against it. |
| Design decisions persist between sessions | `interface-design` | If the project holds its decision file (`.interface-design/system.md`), read it first and build consistently with it; if decisions are made fresh, keep it updated. |
| Web verification (open, screenshot, click, logs) | `webapp-testing` | Stage 4 on web. If unavailable, use browser tooling directly. |
| Web pre-ship audit (a11y, focus, forms, dark mode) | `web-design-guidelines` | Last pass before shipping web UI. Installed via `npx skills add vercel-labs/agent-skills --skill web-design-guidelines`, not as a plugin dependency — if absent, apply the quality rules below instead. |

Two hard rules:

- **One taste engine per task.** `frontend-design` owns aesthetic direction; `ui-ux-pro-max` owns the reference database. Both consulted = conflicting advice. If both are relevant, read frontend-design for direction, use ui-ux-pro-max only for concrete lookups (a palette, a pairing) that serve that direction.
- **This skill arbitrates conflicts.** When a routed skill's advice contradicts the process here (stages, verification, states), the process wins — a skill that skips verification is a worse skill, not a shortcut.

Scope note: every skill in the table is web-centric. Native desktop GUIs (Tkinter, egui, Slint, iced, Qt, Tauri) are covered only by the stages below — that's why this skill exists.

## The four stages, in order

Each stage consumes the output of the previous one. Skipping a stage does not save time — it moves the rework to the end, where it costs more.

### Stage 1 — Compose from existing parts

Before writing any UI element, look for what already exists:

- Components in the codebase: design system, shared widgets, patterns in sibling screens.
- The interface-design file, if present — decisions about buttons, spacing, colors were likely made in a previous session. Rebuilding them fresh is a defect.
- The platform's standard components: native widgets on desktop, `<button>`, `<select>`, `<input>` on web — they carry accessibility and platform behavior for free.
- A mature library only when the standard parts genuinely can't do it, checking what the project already depends on.

Hand-rolling a dropdown, a modal or a date picker the platform provides is a defect, not diligence. And matching sibling screens' patterns matters more than abstract best practice: consistency is invisible quality.

### Stage 2 — Layout system before elements

Decide how things are arranged before styling anything.

- Pick a **spacing scale** (one base unit, e.g. 4px, and its multiples) and use only those values.
- Pick an **alignment model**: a grid for content-heavy pages, flex/stack containers for tool-like UIs, padded containers on desktop.
- Place the structure — headers, sidebars, content areas, gaps, grouping — then fill it.

If you find yourself nudging pixel values to make things "sit right", stop: the layout model is wrong, not the pixels.

### Stage 3 — Deliberate style (routed)

Aesthetics is a decision, not a default — and on web, the decision belongs to `frontend-design`. Consult it and commit to a direction before writing style code.

What remains this skill's own — because it is platform-agnostic and the ready skills are web-only:

- **Tokens, not literals.** Colors, fonts, spacing go through variables/constants (CSS custom properties, theme structs on desktop). Two hardcoded hex values in different files is how themes rot.
- **Dark mode as tokens.** Define colors semantically (surface, text, accent), never as "white text on this blue". Dark mode then falls out for free; without tokens it is a rewrite.
- **Restraint.** One accent color used sparingly beats five colors used evenly; a type scale of 2–3 sizes beats a size per label.
- **Desktop GUIs.** No frontend-design here — apply the same discipline manually: commit to a direction first, prefer the framework's component set, and keep the token rule above.

### Stage 4 — Verify in the running app (run → see → drive)

**Never claim a UI works, looks right, or is fixed unless you have seen it running after the change.** Reading the code is not verification — the render layer is exactly where plausible code diverges from reality.

1. **Run** — start the app (dev server, `cargo run`, `python main.py`).
2. **See** — screenshot the rendered result, compare against the stage-3 intent and, for fixes, against how it looked before.
3. **Drive** — exercise the changed parts: click, submit, resize, toggle theme. Check the states the user will hit, not just the happy path.

On web, route this through `webapp-testing` (Playwright: open, screenshot, click through flows, read logs). On desktop, run the app, capture the window, interact or drive headlessly where the framework allows. If nothing can be captured in the environment, say so plainly — "written but not seen" — never imply it was verified.

Minimum drive: default size, a narrow window (phone width on web), and dark mode where the platform has it. A UI that only works at full width is a broken UI.

## Quality states — cheap to add, costly to skip

A screen shows one of these at any moment; decide what each looks like *before* finishing:

- **Loading** — never a frozen frame; skeleton or busy indicator.
- **Empty** — an empty list is valid; show a message, not a void.
- **Error** — user-readable messages with a recovery action where one exists.
- **Overflow** — long text, many items, no data. Ask "what if this string is 200 characters?" before trusting the layout.

Plus the a11y basics, which standard components mostly give free: labels on inputs, keyboard-reachable actions, contrast on any custom color pair.

## Red Flags

| Thought | Reality |
|---------|---------|
| "No skill needed, I know good design" | Training-data taste is the AI-slop source. Route to the owner for the concern. |
| "I'll use frontend-design and ui-ux-pro-max together" | Two taste engines = conflicting rules, a confused mix. One owner, lookups only. |
| "The markup looks right, done" | Plausible markup ≠ working UI. Run, see, drive. |
| "This is a desktop app, none of the ready skills apply" | True — which is why stages 1–4 and the state rules are yours to follow manually. |
| "I'll add loading/empty states later" | The first empty load is already in production. |
| "It's a tiny change, verification is overkill" | Tiny changes break layouts silently. Run it. |
