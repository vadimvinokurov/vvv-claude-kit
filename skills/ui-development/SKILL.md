---
name: ui-development
description: Playbook for building, modifying, or fixing any user interface - web pages, web apps, and native GUIs (Tauri, egui, Slint, iced, Tkinter, Qt) in any language. Fixes the order of work: look for existing parts first, get the design system from ready skills (frontend-design on web, ui-ux-pro-max lookups), keep decisions in `design.md`, decide states before finishing - and never claim a UI works without seeing it running. Use for ANY UI task, even small ones - a button, a broken layout, a form, a whole screen, "the app looks broken".
---

# UI Development

**Core rule:** never claim a UI works, looks right, or is fixed without seeing it running. Taste belongs to the skills that own it; this skill owns the order of work and the discipline. Do the steps below in order, for any UI task — a button, a broken layout, a whole screen.

**1. Look before you build.**
- Components and patterns already in the codebase first; sibling screens beat abstract best practice.
- Ready-made and template solutions over invented ones — novelty is a cost, not a feature; reach for custom only when nothing existing covers the task.
- If `design.md` exists, its decisions govern — read it, build to it, update it with new decisions.
- Platform stock controls (`<select>`, native widgets, framework component sets) before anything hand-built: hand-rolling a dropdown or modal is a defect, not diligence.

**2. Design system once, then tokens.**
- `ui-ux-pro-max` for the researched system (app type → style, palette, font pairing; on desktop it serves lookups), `frontend-design` on web — read it before any style code. 
- Then write the chosen system as named tokens in the framework's theme system (CSS variables, theme structs), sized to what this UI actually needs — a compact semantic set (surface / text / accent, spacing base, a type scale) beats an exhaustive library.

**3. Layout system before elements.**
- Fix a spacing scale (one base unit + multiples) and an alignment model (grid / stacks / padded containers), then place the structure: headers, sidebars, content, gaps. Nudging pixels to "make it fit" means the model is wrong — fix the model.

**4. States and a11y — the pre-ship audit on every platform.**
- Decide before finishing what each looks like: **loading** (skeleton or indicator, never a frozen frame), **empty** (a message, not a void), **error** (user-readable, with a way back), **overflow** (a 200-character string, a list of 1000 items). Standard components give the a11y basics free — keep them: labels on inputs, keyboard reach, contrast on any custom color pair.
