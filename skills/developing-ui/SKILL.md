---
name: developing-ui
description: Use when building or modifying any user interface — a web page, web app, Tauri app, or native GUI (egui, Slint, iced, Tkinter, Qt) — in any language. Covers the whole UI development path: compose from existing components first, follow a consistent layout system, pick aesthetics deliberately, then prove the result with a run-see-drive loop (the "wrote the code, never ran it" gap). Triggers: "build/make/fix a UI", "add a form/button/page", "layout/style change", "component", "desktop GUI", "egui", "slint", "tauri", "webpage".
---

# Developing UI — exist, compose, style, verify

**Core rule:** a UI change is done only when it (1) reuses what the project already has, (2) follows one consistent layout system, (3) has a deliberate aesthetic direction, and (4) has been **run, seen, and driven** with logs read. "It compiles", "typecheck passed", "looks right in the code" satisfy none of the four.

## 1. Use what exists — never hand-roll what is already built

Before writing any control or screen from scratch:

- **Check the project first**: which UI/framework stack does it already use, which component set is installed (shadcn/ui, MUI, Ant, Naive UI; egui widgets, Slint built-ins, Tkinter ttk)? Use those components — the same button types, the same patterns as neighboring screens. Match existing style even if you'd do it differently.
- **Ready-made before hand-written**: a standard control (button, input, select, dialog, table, toast) comes from the component library or framework primitives. Hand-rolling is justified only when no ready element covers the case — and then it should visually sit inside the existing system.
- **Check the library before guessing APIs**: use context7 (or the component docs) for the actual props/variants — do not invent component APIs.
- **Tokens, not values**: colors, spacing, radii, font sizes come from the project's existing variables/scale (CSS vars, theme, design tokens). If none exist, define one small scale up front (spacing 4/8/16/32, one font stack, 2–3 colors + one accent) and stick to it — do not invent ad-hoc values per screen. When the `ui-ux-pro-max` plugin is installed, generate the missing token base with its design-system output (MASTER.md + DTCG/CSS variables) instead of inventing it by hand.
- **Blocks and templates before from-scratch composition**: for a standard screen (login, dashboard, settings, form), look first in the "Where to look" section below and adapt a ready block; if the block's format doesn't fit the project (e.g. a Tailwind block in a plain-CSS project, a Slint gallery for an egui app), use it as a live reference — open the sample page, screenshot it as the target direction, reproduce it with the project's components. Inventing a standard screen from an empty file is the last resort.

## Where to look for ready-made

Web and Tauri (webview):

| Source | URL | What |
|---|---|---|
| shadcn/ui blocks | https://ui.shadcn.com/blocks | Login, dashboard, sidebar compositions; `npx shadcn add <block>`, free |
| Bootstrap examples | https://getbootstrap.com/docs/5.3/examples/ | Whole pages: dashboards, checkout, pricing, sign-in |
| Flowbite blocks | https://flowbite.com/blocks/ | Sections: hero, forms, tables, navigation (HTML + Tailwind) |
| daisyUI components | https://daisyui.com/components/ | ~68 ready components, open source |
| MUI templates | https://mui.com/material-ui/getting-started/templates/ | Ready pages for React stacks |
| Ant Design Pro | https://pro.ant.design | Enterprise dashboard patterns |
| Tailwind Plus (ex-Tailwind UI) | https://tailwindcss.com/plus | Professionally designed blocks — paid, only if the project already licenses it |

Rust GUI:

| Source | URL | What |
|---|---|---|
| egui examples | https://github.com/emilk/egui/tree/main/examples | file_dialog, images, multiple_viewports, screenshot, … |
| Slint demos | https://slint.dev/demos | Weather/Energy/Printer demos + widget galleries in Material and Fluent design |
| iced examples | https://github.com/iced-rs/iced/tree/master/examples | tour, todos, styling (light/dark), clock, … |

## 2. Composition and layout rules

- **One layout system per screen**: a single direction of flow (column, or rows in a column), consistent alignment axis; absolute positioning only for true overlays (dialogs, badges) — never as layout.
- **Semantic structure**: real containers and semantics (nav/main/section + headings on web; idiomatic widget hierarchies in native GUIs; labels tied to inputs; logical tab/focus order).
- **Spacing rhythm from the scale** (section of §1): padding inside a card is one unit, gap between cards the next; whitespace groups related content and separates unrelated — proximity before extra borders.
- **Responsive by constraint**: content wraps or reflows at narrow widths; nothing clips. Test the narrow case (see the ~500px trap in §4). On native: design the layout for resizable windows, min sizes included.
- **States and edges**: every interactive element has hover/focus/active/disabled states; empty, loading, error, and very-long-value cases are designed, not ignored.
- **One visual language**: one accent color, one weight for emphasis, one border radius per role. Every decorative choice is borrowed from the existing screens or the chosen direction — not a new idea per screen.

## 3. Aesthetics — deliberate, not default

For the *look* (typography, palette, personality), invoke `frontend-design:frontend-design` first: it forces a subject and visual direction before code. Then, when the `ui-ux-pro-max` plugin is installed, use it for what it is: a searchable reference — `ui-ux-pro-max:ui-ux-pro-max` for picking concrete style, palette and font pairing from its catalogs (don't invent them from thin air) and its pre-style anti-pattern checks (contrast, focus states, no emoji-as-icons) as the §2 polish list. Take the direction from frontend-design; take the concrete values from the search or the project tokens — never both engines competing for the same decision. This section's rules keep the result consistent; frontend-design keeps it from reading as a templated default.

## 4. The verify loop — run it, see it, drive it

A UI change is **not done** until the changed UI has been **run, seen, and driven** in a real or headless runtime, and its console/runtime logs read:

1. **Run** — the real thing: dev/static server for web; the app binary or test harness for a native GUI.
2. **See** — an image or accessibility snapshot of the actual rendered UI, whole window first:
   - Web / Tauri (webview): Playwright MCP — `browser_navigate` to the server URL → `browser_take_screenshot` (full page). If the MCP server is unavailable in the environment, substitute an equivalent tool with the same evidence: a minimal Playwright (Node/Python) script driving headless Chromium, or `chrome --headless --screenshot` — same loop, same artifacts.
   - egui: `egui_kittest` — harness snapshot returns both the image and an AccessKit snapshot of the whole UI.
   - Any app that can render itself into a buffer on command: that buffer — rendered offscreen by the app's own renderer through its control channel, not a capture of the physical screen.
   - Nothing of the above is possible? The work stays **verifiably unfinished**: say so explicitly and list what could not be checked. It does not silently become "done".
3. **Drive** — exercise the interactive paths you changed or added: click, submit, type, resize smaller (Playwright MCP: `browser_click`, `browser_type`, `browser_resize`; egui: kittest queries and clicks).
4. **Read the logs** — browser console: `browser_console_messages`; native: app stdout/stderr, framework warnings, panics. Zero errors is the bar.
5. **Fix and repeat** — anything found in steps 2–4 goes back through step 1. The loop ends on a full clean pass.

Report honestly: what you ran, the evidence (screenshot/snapshot paths), what you drove, what the logs said — or exactly what remains unverified.

Two capture traps, proven on a live run: a full-page screenshot taken immediately after a click can show a stale frame (old state still rendered) — wait for the UI to settle before capturing, and confirm suspicion with an element-level check before calling it a bug; and Chrome will not open windows narrower than ~500 CSS px — the viewport silently clamps and the screenshot at the ordered width gets cropped, so verify narrow layouts with a wide window plus a `scrollWidth` measurement.

Per-stack quick reference:

| Stack | Run | See | Drive | Logs |
|---|---|---|---|---|
| Web page/app | static or dev server | Playwright MCP: navigate + screenshot | browser_click / browser_type / browser_resize | browser_console_messages |
| Tauri | `tauri dev` → localhost URL | same as web (on the dev server URL) | same as web | browser_console_messages + app stdout |
| egui | app binary or egui_kittest harness | egui_kittest snapshot (image + AccessKit snapshot) | kittest queries / clicks | stdout/stderr, panics |
| Slint / others | app binary | offscreen render into a buffer via the app's own control channel; framework tooling where it exists | framework tooling | stdout/stderr |

## Red flags

- "I'll just write a custom button/div instead of the library component" — reuse first (§1).
- "I didn't check what the project already uses" — a new screen must sit inside the existing system, not beside it (§1).
- "It's a small/trivial change" — the loop is the same size (§4).
- "Build/typecheck passed" — the compiler did not click anything (§4).
- "The code looks correct" — reading code is not seeing the UI (§4).
- "No browser/display available, skipping the check" — say "not verified, and here is why"; never silently skip (§4).
- One screenshot at the very end of all work instead of loop iterations per defect — that is a postcard, not a loop (§4).
- "The user will see it anyway" — the user is not your test harness (§4).

Return to the sections: exist → compose → style → verify (run → see → drive → logs → fix).
