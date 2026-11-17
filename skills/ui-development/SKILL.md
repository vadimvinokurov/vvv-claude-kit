---
name: ui-development
description: Process for building, modifying, or fixing any user interface - web pages, web apps, and native GUIs (Tauri, egui, Slint, iced, Tkinter, Qt) in any language. Orchestrates the ready-made UI skills (frontend-design for taste, ui-ux-pro-max for style references, webapp-testing for verification, interface-design for decision memory, web-design-guidelines for the pre-ship audit) on top of the four-stage process: compose from existing parts, layout before style, deliberate style, verify in the running app. Use for ANY UI task, even small ones - adding a button, fixing a layout, styling a form, building a screen, or "the app looks broken".
---

# UI Development

**Core idea:** never work blind. Route taste to the skills installed for it, follow the four stages, and never claim a UI works without seeing it running. This skill is the coordinator — it carries no taste of its own.

## Ready skills first — one owner per concern

One owner per concern; the platform decides who owns it:

- **Taste** (aesthetic direction, typography) — web: `frontend-design`, read it at stage 3, always. Desktop: no ready skill owns taste — commit to a direction manually (stage 3), with `ui-ux-pro-max` style/palette lookups as reference.
- **Design system from scratch** — `ui-ux-pro-max`: consulted once for a researched system (styles, palettes, font pairings, per-stack reasoning for 20+ web/mobile stacks). Desktop stacks aren't among them — there it serves lookups (palette, pairing) only.
- **Cross-session consistency** — `interface-design`, platform-agnostic: if `.interface-design/system.md` exists, read it first; else keep it updated with decisions made.
- **Verification** (open, screenshot, click, logs) — if the stack ships a harness that covers this, use it: web → `webapp-testing` (Playwright), egui → `egui_kittest` (accessibility tree). No harness → Playwright MCP / browser tooling; Tauri's UI is web code, so those tools reach its web layer too. Everything else — run + capture.
- **Pre-ship audit** (a11y, focus, forms, dark mode) — web: `web-design-guidelines`, not a plugin dependency (`npx skills add vercel-labs/agent-skills --skill web-design-guidelines`); absent → the quality rules below. Desktop: the quality rules below are the audit.

Never run two taste engines — conflicting rules produce a confused mix. When routed advice contradicts this process (stages, verification), this process wins.

## Desktop framework: agent-testable first

If the desktop stack is not already fixed, pick it by one criterion: **can an agent see and drive this UI?**

- **Web-layer GUIs (Tauri)** — web tools see and click the UI; full e2e via WebDriver (macOS desktop WebDriver is limited).
- **egui** — official `egui_kittest` drives the UI by accessibility tree (`get_by_label`, clicks, state asserts).
- **Other toolkits (Tkinter, Slint, iced, Qt)** — only if the project already uses them or the user picks them; otherwise every check degrades to "written but not seen".

## The four stages

1. **Compose** — find before build: codebase components, `.interface-design/system.md` if present, platform standard controls, then libraries matching existing dependencies. Hand-rolling a stock dropdown or modal is a defect. Sibling-screen patterns beat abstract best practice.
2. **Layout** — pick a spacing scale (one base unit + multiples) and an alignment model (grid / flex stacks / padded containers) before placing any element. Nudging pixels to "fix the fit" means the layout model is wrong — fix the model.
3. **Style** — web: commit to a direction via `frontend-design` before writing style code. Own rules, all platforms: tokens over literals (CSS variables, theme structs — this is how dark mode and theming stay free), one accent color, 2–3 type sizes. Desktop does the direction choosing manually.
4. **Verify (run → see → drive)** — run the app, screenshot the rendered result, then drive the change: click it, submit it, resize to phone width, toggle dark mode. Use the harness that covers it (see Verification above); if nothing is capturable, say "written but not seen" — never imply it was verified.

## States — decide before finishing

What each looks like, not just the happy path: **loading** (skeleton or busy indicator, never a frozen frame), **empty** (a message, not a void), **error** (user-readable, with a way back), **overflow** (a 200-character string, a list of 1000 items). A11y basics come free from standard components: labels on inputs, keyboard reach, contrast on custom color pairs. Web-only pre-ship: `web-design-guidelines`.

## Red flags

- "Markup looks right, done" → plausible ≠ rendered. Run, see, drive.
- "I know good design, no skill needed" → training-data taste is the AI-slop source.
- "Use frontend-design and ui-ux-pro-max together" → two taste engines, conflicting rules.
- "Any desktop framework will do" → an unverifiable UI is "written but not seen" forever.
- "It's tiny, verification is overkill" → tiny changes break layouts silently.
- "States later" → the first empty load is already in production.
