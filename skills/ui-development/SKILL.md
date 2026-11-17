---
name: ui-development
description: Guidance for building, modifying, or fixing any user interface - web pages, web apps, and native GUIs (Tauri, egui, Slint, iced, Tkinter, Qt) in any language. Establishes the four-stage process (compose from existing parts, build the layout system, apply style deliberately, verify in the running app) plus layout, verification, and quality rules. Use for ANY UI task, even small ones - adding a button, fixing a layout, styling a form, building a screen, or "the app looks broken" - not just full pages from scratch.
---

# UI Development

**Core idea:** a working UI is never assumed — it is *seen*. The most common failure in agent-driven UI work is writing markup that looks plausible in code but falls apart when rendered. This skill closes that gap with a fixed process and a verification loop.

Scope: any UI — a web page, a web app, a Tauri app, or a native GUI (egui, Slint, iced, Tkinter, Qt). Applies to building from scratch, adding to an existing UI, and fixing a broken one.

## The four stages, in order

Each stage consumes the output of the previous one. Skipping a stage does not save time — it moves the rework to the end, where it costs more.

### Stage 1 — Compose from existing parts

Before writing any UI element, look for what already exists:

- Components already in the codebase (design system, shared widgets, copy-pasted patterns in sibling screens).
- The platform's standard components: native widgets on desktop, `<button>`, `<select>`, `<input>` on web. Standard controls get accessibility, keyboard navigation and platform behavior for free.
- A mature library only when the standard parts genuinely can't do it — picked after checking what the project already depends on.

Hand-rolling a dropdown, a modal or a date picker that the platform provides is a defect, not diligence. Read sibling screens first: matching *their* patterns matters more than matching abstract best practice, because consistency is invisible quality.

### Stage 2 — Layout system before elements

Decide how things are arranged before styling anything.

- Pick a **spacing scale** (one base unit, e.g. 4px, and multiples of it) and use only those values.
- Pick an **alignment model**: a grid for content-heavy pages, flex/stack containers for tool-like UIs, containers with padding on desktop GUIs.
- Place the structure — headers, sidebars, content areas, gaps, grouping — and only then fill it.

If you find yourself nudging pixel values to make things "sit right", stop: the layout model is wrong, not the pixels.

### Stage 3 — Deliberate style

Aesthetics is a decision, not a default. Before styling, state (even one line is enough) what the UI should feel like — dense and utilitarian, friendly and rounded, stark and typographic — and then make every style choice serve that.

- **Tokens, not literals.** Colors, fonts and spacing go through variables/constants (CSS custom properties, theme structs on desktop). Two hardcoded hex values in different files is how themes rot.
- **Type hierarchy with few choices.** One font family, 2–3 sizes, weights and color for emphasis. Every label getting its own size or color is noise, not hierarchy.
- **Dark mode as tokens.** If the platform supports dark mode, define colors as semantic tokens (surface, text, accent) — never as "white text on this blue". Dark mode then falls out for free; without tokens it is a rewrite.
- **Restraint.** One accent color, used sparingly, beats five colors used evenly.

### Stage 4 — Verify in the running app (run → see → drive)

**The rule: never claim a UI works, looks right, or is fixed unless you have seen it running after the change.** Reading the code is not verification — the render layer is exactly where plausible code diverges from reality.

1. **Run** — start the app (dev server, `cargo run`, `python main.py`, whatever the project uses).
2. **See** — screenshot or describe the actual rendered result after the change. Compare against the intent from stage 3, and against what it looked like before for fixes.
3. **Drive** — exercise the changed parts: click the button, submit the form, resize the window, toggle the theme. Check the states the user will hit, not just the happy path.

For web UIs the browser tooling (navigate, screenshot, click, resize, console) does all three; for desktop GUIs, run the app, capture the window, and interact or drive headlessly where the framework allows it. If nothing can be captured in the environment, say so plainly — "written but not seen" — instead of implying it was verified.

What to drive at minimum: default size, a narrow window (or phone width on web), and — where the platform has it — dark mode. A UI that only works at full width is a broken UI.

## Quality states — cheap to add, costly to skip

A screen shows one of these at any moment; decide what each looks like *before* finishing:

- **Loading** — never a frozen frame; placeholder/skeleton or a busy indicator.
- **Empty** — an empty list is a valid state; show a message or an empty-state hint, not a void with no explanation.
- **Error** — user-readable messages with a recovery action where one exists.
- **Overflow** — long text, many items, no data at all. Ask "what if this string is 200 characters?" before assuming the layout survives.

Plus the basics of access, which mostly come free from standard components: labels on inputs, keyboard-reachable actions, contrast on text — verify contrast whenever a custom color pair is introduced.

## Red Flags

| Thought | Reality |
|---------|---------|
| "The markup looks right, done" | Plausible markup ≠ working UI. Run, see, drive. |
| "I'll add loading/empty states later" | Later never comes; the first empty load is already in production. |
| "Two colors, I'll hardcode them" | Tokens now, or dark mode/theming is a rewrite later. |
| "No need to check existing components" | Divergent patterns in sibling screens are user-visible inconsistency. |
| "It's a tiny change, verification is overkill" | Tiny changes break layouts silently. Run it. |
| "Nudging 2px here and there" | The layout model is wrong; fix the model, not the pixels. |
