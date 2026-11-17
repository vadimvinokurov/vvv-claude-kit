---
name: ui-development
description: Playbook for building, modifying, or fixing any user interface - web pages, web apps, and native GUIs (Tauri, egui, Slint, iced, Tkinter, Qt) in any language. Fixes the order of work: look for existing parts first, choose an agent-testable desktop stack, get the design system from ready skills (frontend-design on web, ui-ux-pro-max lookups, interface-design for decision memory), decide states before finishing, verify by running the app (framework harness, else Playwright MCP) - never claim a UI works without seeing it. Use for ANY UI task, even small ones - a button, a broken layout, a form, a whole screen, "the app looks broken".
---

# UI Development

**Core rule:** never claim a UI works, looks right, or is fixed without seeing it running. Taste belongs to the skills that own it; this skill owns the order of work and the discipline. Do the steps below in order, for any UI task — a button, a broken layout, a whole screen.

**1. Look before you build.**
Components and patterns already in the codebase first; sibling screens beat abstract best practice. If `.interface-design/system.md` exists, its decisions govern — read it, build to it, update it with new decisions. Platform stock controls (`<select>`, native widgets, framework component sets) before anything hand-built: hand-rolling a dropdown or modal is a defect, not diligence.

**2. Desktop stack: agent-testable first** (only when the project doesn't already fix it). The criterion: can an agent see and drive this UI?
- **Web-layer GUIs** — Tauri (Rust), Electron, Wails, Neutralino: the UI is a web app, so web tools drive it; e2e via WebDriver (macOS desktop WebDriver is limited).
- **egui** — official `egui_kittest`: drives by accessibility tree (`get_by_label`, clicks, state asserts).
- **Everything else** (Tkinter, Slint, iced, Qt) — only when the project already uses it or the user picks it; every check then degrades to run + capture.

**3. Design system once, then tokens.**
Consult `ui-ux-pro-max` once for the researched system: app type → style, palette, font pairing (full per-stack reasoning covers web/mobile stacks; on desktop it serves as lookups). On web the aesthetic direction itself comes from `frontend-design` — read it before any style code. Then write tokens in the framework's theme system (CSS variables, theme structs): surface / text / accent, spacing base, 2–3 type sizes, one accent color, dark mode from the same tokens. Hardcoded colors in two files is how themes rot.

**4. Layout system before elements.**
Fix a spacing scale (one base unit + multiples) and an alignment model (grid / stacks / padded containers), then place the structure: headers, sidebars, content, gaps. Nudging pixels to "make it fit" means the model is wrong — fix the model.

**5. Verify: run → see → drive.**
Run the app, screenshot the rendered result, compare against the intent from step 3 (and against the before-state for fixes). Then drive the change: click it, submit it, resize to phone width / narrow window, toggle dark mode. Use the harness that covers it — `egui_kittest` on egui, Playwright MCP / browser tooling on web and web-layer GUIs; run + capture on the rest. Nothing capturable → say "written but not seen", never imply verification.

**6. States and a11y — the pre-ship audit on every platform.**
Decide before finishing what each looks like: **loading** (skeleton or indicator, never a frozen frame), **empty** (a message, not a void), **error** (user-readable, with a way back), **overflow** (a 200-character string, a list of 1000 items). Standard components give the a11y basics free — keep them: labels on inputs, keyboard reach, contrast on any custom color pair.

Two binding rules across all steps: **one taste engine per task** — `frontend-design` owns web direction, `ui-ux-pro-max` serves lookups; running both as taste engines yields conflicting rules. And **this process arbitrates**: routed advice that skips verification loses.

## Red flags

- "Markup looks right, done" → plausible ≠ rendered. Run, see, drive.
- "I know good design, no skill needed" → training-data taste is the AI-slop source.
- "Any desktop framework will do" → an unverifiable UI is "written but not seen" forever.
- "It's tiny, verification is overkill" → tiny changes break layouts silently.
- "States later" → the first empty load is already in production.
