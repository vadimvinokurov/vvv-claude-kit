---
name: building-testable-apps
description: Use when starting any application development (new app, new feature in an app, architectural refactor) — user rule: every app under development must follow these seven headless-development rules (usually required in the project CLAUDE.md). Triggers: "create an app", "add a feature", "write a CLI/Tkinter/web app", "build a game/utility/service".
---

# Building Testable Apps — 7 Rules of Headless Development

**Core idea:** an app = a pure library + auto-generated UI. The agent can verify any feature by invoking a command, with no screen.

A feature is **not done** until all seven rules below pass. This is discipline, not a recommendation.

## The seven rules (acceptance checklist)

1. **Headless-First Core** — all logic lives in pure modules: they take data structures in, return data structures/buffers. Zero imports of UI/browser/windowing APIs in the core. Acceptance example: the algorithm is invoked from a console command with no screen initialization.
2. **Schema-Driven Commands** — every operation is described by a contract: `{id, params schema (validation), pure handler}`. Forms, controls and UI validators are **generated** from these schemas. A new feature = one structure + one handler; hand-writing UI for a feature is a violation.
3. **Dual-Path Oracle** — **Applies when:** the core contains a non-obvious or optimized algorithm. Then every such algorithm is duplicated by a naive reference implementation (as direct and mathematically strict as possible), and the test runner feeds identical inputs to both and checks Δ ≤ ε. Plain CRUD/orchestration — where the implementation is already the naive one — has no such algorithms, so the rule does not apply; that is no reason to skip the other rules.
4. **Golden Master Corpus** — **Applies when:** the core processes or transforms **data artifacts** (files, bytes, media/pixel data, complex formats) or reproduces or ports the behavior of an existing system. If the core is pure CRUD/orchestration, this rule does not apply: ordinary state and serialization tests are enough — no reason to skip the remaining six rules.
   When it applies: tests are checked against external reference files (golden JSON, bytes, snapshots), not just mocks. Invariant: read the reference → run the engine → byte-wise/differential comparison. If an original reference system exists, its outputs are the golden files. If none exists (a new app): the corpus is fixed as regression baselines plus **at least one case computed by hand**, independently of the engine — a corpus generated entirely by the engine itself is not allowed. Note the boundary: a file the app only uses to persist its own state is trivial serialization, not artifact processing — artifact processing means the core's subject matter is transforming complex formats/media/bytes.
5. **Strict Type Invariants** — linter/compiler: no `any`/`as` casts/suppressed warnings/uncontrolled coercions. The feature is not done until the strict check passes; "configured, but never run" = not done.
6. **Headless Control Interface** — two independent halves; each applies on its own:
   - **Text RPC — always, for any stateful app.** A text RPC/CLI covers everything interactively stateful: state snapshots and command access to every interactive capability, no window needed. Component hierarchy is verified through it.
   - **Screen rendering — only for apps with a visual screen.** **The render target is the source of visual truth:** the screen can "render itself" into a buffer (PNG/bytes) on command — rendered by the app's own renderer, not by the OS grabbing the screen (photocraft pattern: "every screenshot is the real app, rendered offscreen through its control channel"). Two legal image sources for acceptance: (1) the app's own window rendering itself into a buffer; (2) if the window cannot render itself offscreen — its page rendered by a headless browser with external APIs stubbed. Filming the physical screen (a monitor with foreign windows, a cursor, desktop state) is forbidden: it is non-deterministic, carries extra content, and in a headless environment is unavailable.
7. **Visual Acceptance (GUI)** — **mandatory visual check of the window after any edit to its UI.** Changed anything the user will see on screen (a window, page, dialog, email template): the window is accepted **as a whole and only visually** — get a shot of the whole window from the rule-6 sources in their priority order (render into a buffer → page stub + headless browser) at the real window sizes (+ margin) → **read the shot with your own eyes: all elements visible, nothing cropped, texts legible**; if the appearance changed — before/after shots plus a verbal diff. Checking "only the changed fragments" is not acceptance: cropping lives in untouched zones too. Any shot from rule 6 does not cover the fact of a real window: the actual size and min-clamps at open time, the titlebar/chrome, the build config's ACL/permissions, third-party plugin defaults — these defect classes exist only on the live screen; what the shot cannot see stays on the live check (§11.2, a p.7-like manual list).

## Quick reference — accepting a feature

| Check | How |
|---|---|
| Core isolated? | grep the core for UI/OS imports; invoke the algorithm from the CLI |
| Command contract? | Command registry, a params schema per operation, UI built from the registry |
| Oracle? | Naive version + a Δ ≤ ε test on identical inputs |
| Golden corpus? | Is it needed? Does the core contain algorithms over data artifacts (files/bytes/media/formats) or reproduction of an existing system? No → skip the rule. Yes → reference files in the repo, test-runner compares engine output against them (+1 hand-computed case) |
| Strict checks run? | `npm run typecheck` / `mypy --strict` / `ruff --strict` — an actual run, not "configured" |
| Headless control? | A `snapshot` command gives state; a render command gives a buffer with no window |
| Visual acceptance? | After editing a window's UI: the whole window. Image source, in order of preference: app render into a buffer (rule 6) → page stub + headless screenshot (fallback for screens that cannot render offscreen); read it; appearance change — before/after |

Visual acceptance recipe (proven on a live Tauri client case, 2026-11-06):
copy the page into a separate file, add a stub `window.__TAURI__` (or another
windowing API) with test values; take
`Chrome --headless --screenshot --force-device-scale-factor=1 --window-size=<window width>,<window height>`
and **read** the shot. Trap: Chrome will not open windows narrower than ~500 CSS px —
the viewport silently clamps, and the screenshot at the ordered width gets cropped;
"cropping" wider than ~500 on the shot is a tool artifact, not the page — verify
with a wide window and a `scrollWidth` measurement.

## Red flags — the feature is not done

- UI code hand-written for a specific feature ("faster to hardcode the form")
- Tests checked only against mocks/itself — where an oracle/golden applies (the predicate in rule 4)
- mypy/tsc/warnings-as-errors configured but never actually run to completion for the feature
- "Simpler to do it by hand", "it's a small project", "golden files later", "types later"
- "I'd just open the window and check — why headless snapshots"
- Dynamic typing / `# type: ignore` / `any`, just "to close the error"
- "I'll check manually in the browser, unit tests are enough"
- "I set the window size by calculation, the content will fit" — without a read screenshot it is not acceptance
- "The edit is small/purely cosmetic, no screenshot needed" — rule-7 acceptance does not depend on the diff size

**All of these thoughts = a rule violation. Stop, return to the structure: core → contracts → oracle → golden → strict → headless interface.**

## Common mistakes

- Generate the UI from schemas but hardcode handlers in the UI code → the handler lives only in the command registry.
- Golden files generated by your own implementation after the feature → at least one reference is computed by hand (or taken from the original system/reference source); the rest are the regression corpus.
- An oracle optimized "just a little" → the oracle must be the maximally dumb implementation.
- Strict mode disabled for "difficult" folders → a feature in such a folder is not done.

See also: superpowers:test-driven-development (order: test → core → oracle → golden), superpowers:verification-before-completion (the strict run as proof).
