---
name: ui-development
description: Playbook for building, modifying, or fixing any user interface - web pages, web apps, and native GUIs (Tauri, egui, Slint, iced, Tkinter, Qt) in any language. Fixes the order of work: look for existing parts first, get the design system from ready skills (frontend-design on web, ui-ux-pro-max lookups), keep decisions in `doc/design.md`, decide states before finishing, verify by running the app with an agent-testable stack (framework harness, else Playwright MCP) - never claim a UI works without seeing it. Use for ANY UI task, even small ones - a button, a broken layout, a form, a whole screen, "the app looks broken".
---

# UI Development

**Core rule:** never claim a UI works, looks right, or is fixed without seeing it running. Taste belongs to the skills that own it; this skill owns the order of work and the discipline. Do the steps below in order, for any UI task — a button, a broken layout, a whole screen.

**1. Look before you build.**
Components and patterns already in the codebase first; sibling screens beat abstract best practice. Ready-made and template solutions over invented ones — novelty is a cost, not a feature; reach for custom only when nothing existing covers the task. If `doc/design.md` exists, its decisions govern — read it, build to it, update it with new decisions. Platform stock controls (`<select>`, native widgets, framework component sets) before anything hand-built: hand-rolling a dropdown or modal is a defect, not diligence.

**2. Design system once, then tokens.**
Consult `ui-ux-pro-max` once for the researched system: app type → style, palette, font pairing (full per-stack reasoning covers web/mobile stacks; on desktop it serves as lookups). On web the aesthetic direction itself comes from `frontend-design` — read it before any style code. Then write tokens in the framework's theme system (CSS variables, theme structs): surface / text / accent, spacing base, 2–3 type sizes, one accent color, dark mode from the same tokens. Hardcoded colors in two files is how themes rot.

**3. Layout system before elements.**
Fix a spacing scale (one base unit + multiples) and an alignment model (grid / stacks / padded containers), then place the structure: headers, sidebars, content, gaps. Nudging pixels to "make it fit" means the model is wrong — fix the model.

**4. Verify: run → see → drive.**
If the project doesn't fix the desktop stack, pick an agent-testable one (web-layer GUI or egui) — this step depends on it. Run the app, screenshot the rendered result, compare against the intent from step 2 (and against the before-state for fixes). Then drive the change: click it, submit it, resize to phone width / narrow window, toggle dark mode. Use the harness that covers it — `egui_kittest` on egui, Playwright MCP / browser tooling on web and web-layer GUIs; run + capture on the rest. Nothing capturable → say "written but not seen", never imply verification.

**5. States and a11y — the pre-ship audit on every platform.**
Decide before finishing what each looks like: **loading** (skeleton or indicator, never a frozen frame), **empty** (a message, not a void), **error** (user-readable, with a way back), **overflow** (a 200-character string, a list of 1000 items). Standard components give the a11y basics free — keep them: labels on inputs, keyboard reach, contrast on any custom color pair.
