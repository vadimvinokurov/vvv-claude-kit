---
name: building-testable-apps
description: Teaches seven headless-development rules — build every app as a pure, verifiable core library with a thin auto-generated UI, so the agent can test any feature by running commands with no screen. Use when the user asks to create a new application, module, feature, CLI, game, utility, or service, or says "create an app", "add a feature", "write a CLI/Tkinter/web app", "build a game/utility/service". Do not use for refactoring, fixing, or other changes to existing code unless the user explicitly asks to apply this skill — existing code is never rewritten to conform to these rules without an explicit request.
---

# Building Testable Apps — 7 Rules of Headless Development

**Core idea:** an app = a pure library + auto-generated UI. The agent can verify any feature by invoking a command, with no screen.

A feature is **not done** until all seven rules below pass. This is discipline, not a recommendation.

## Scope — new code only

These rules govern code that is written **new**: a new app, a new module, a new feature. If the task is to refactor, fix, or modify existing code, this skill applies only when the user explicitly asked to apply it — and even when it applies, existing code is not rewritten to conform to these rules unless the user explicitly requested that rewrite. New code added inside an existing system follows the rules; the surrounding legacy code is left as is.

## The seven rules (acceptance checklist)

1. **Headless-First Core** — all logic lives in pure modules: they take data structures in, return data structures/buffers. Zero imports of UI/browser/windowing APIs in the core. Acceptance example: the algorithm is invoked from a console command with no screen initialization.
2. **Schema-Driven Commands** — every operation is described by a contract: `{id, params schema (validation), pure handler}`. Forms, controls and UI validators are **generated** from these schemas. A new feature = one structure + one handler; hand-writing UI for a feature is a violation.
3. **Dual-Path Oracle** — **Applies when:** the core contains a non-obvious or optimized algorithm. Then every such algorithm is duplicated by a naive reference implementation (as direct and mathematically strict as possible), and the test runner feeds identical inputs to both and checks Δ ≤ ε. Plain CRUD/orchestration — where the implementation is already the naive one — has no such algorithms, so the rule does not apply; that is no reason to skip the other rules.
4. **Golden Master Corpus** — **Applies when:** the core processes or transforms **data artifacts** (files, bytes, media/pixel data, complex formats) or reproduces or ports the behavior of an existing system. If the core is pure CRUD/orchestration, this rule does not apply: ordinary state and serialization tests are enough — no reason to skip the remaining six rules.
   When it applies: tests are checked against external reference files (golden JSON, bytes, snapshots), not just mocks. Invariant: read the reference → run the engine → byte-wise/differential comparison. If an original reference system exists, its outputs are the golden files. If none exists (a new app): the corpus is fixed as regression baselines plus **at least one case computed by hand**, independently of the engine — a corpus generated entirely by the engine itself is not allowed. Note the boundary: a file the app only uses to persist its own state is trivial serialization, not artifact processing — artifact processing means the core's subject matter is transforming complex formats/media/bytes.
5. **Strict Type Invariants** — linter/compiler: no `any`/`as` casts/suppressed warnings/uncontrolled coercions. The feature is not done until the strict check passes; "configured, but never run" = not done.
6. **Headless Control Interface** — two independent halves; each applies on its own:
   - **Text RPC — always, for any stateful app.** A text RPC/CLI covers everything interactively stateful: state snapshots and command access to every interactive capability, no window needed. Component hierarchy is verified through it.
   - **Screen rendering — only for apps with a visual screen.** The render target is the source of visual truth: the screen "renders itself" into a buffer (PNG/bytes) on command — through the app's own renderer, not an OS grab of the screen. Two legal image sources for acceptance, in priority order: (1) the app's own window rendering itself into a buffer; (2) if it cannot render offscreen — its page rendered by a headless browser with external APIs stubbed. Filming the physical screen is forbidden: it is non-deterministic, carries foreign content (other windows, cursor, desktop state), and is unavailable in a headless environment.
7. **Visual Acceptance (GUI)** — **mandatory visual check of the window after any edit to its UI.** Changed anything the user will see on screen (a window, page, dialog, email template):
   - Accept the window as a whole, visually only: get the whole-window shot from the rule-6 sources in their priority order (render into a buffer → page stub + headless browser) at the real window sizes (+ margin).
   - Read the shot with your own eyes: all elements visible, nothing cropped, texts legible.
   - Appearance change → before/after shots plus a verbal diff.
   - Checking "only the changed fragments" is not acceptance — cropping lives in untouched zones too.
   - A rule-6 shot does not cover the fact of a real window: the actual size and min-clamps at open time, the titlebar/chrome, the build config's ACL/permissions, third-party plugin defaults. What the shot cannot see stays on the live check.
