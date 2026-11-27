---
name: subagent-rules
description: Duties of a spawned subagent — load when the spawn prompt told you to, as your first action, before any work. Budget as an alarm, tracker checkpoints, no sleep-polling, report with gate outputs.
---

# Subagent Rules — being the spawned agent

Load order: read your tracker item + the context it points to first; the
working tree is the truth when the plan and the tree diverge.

1. **Budget is an alarm, not a quota.** Nearing the stated budget: post a
   tracker note (what is done, what remains), then stop — or ask the
   coordinator for ONE extension with a stated ceiling. Never silently grow
   or split the task.
2. **Checkpoint at every milestone**, mid-task included — a dead agent with
   tracker notes is a 5-minute restart; without notes, a total loss.
3. **Detach background waits.** Wake on the completion notification; no
   sleep-polling — each poll round pays your whole context for zero output.
   A wait over ~2 min goes back as "background, id X".
4. **Report gate outputs, not claims:** files changed; gates with actual
   outputs (command, counts, exit codes) — "all green" is not reporting.
   When you spawn a sub-agent yourself: verified model names or defaults —
   no unverified overrides.
5. Session-side economics (reading, gates schedule, edit discipline) apply
   to you as well: they are `token-economy` — load it if your context
   lacks it.
