---
project: "[Your Project Name]"
status: scaffold           # design | building | shipped | maintenance | paused
phase: "[Phase / milestone]"
last_updated: YYYY-MM-DD
next_gate: "[Next decision or milestone]"
blocked_on: null           # short string, or null
---

# [Your Project Name] — status

## Current

One paragraph describing where the project is right now: what just shipped,
what is actively being built, and the immediate next milestone.

## Recent (last 7 days)

- Bullet of meaningful changes (commits, decisions, gates passed).
- Keep to ≤ 5 items. Older history lives in git log.

## Next

- 1–3 next concrete actions. Reference files, issues, or PRs.

## Blocked / waiting

- Anything stalled and what it is waiting on. Leave an empty bullet if nothing is blocked.

## Pointers

- PRD: `docs/1_product/PRD.md`
- TRD: `docs/2_architecture/TRD.md`
- SDD: `docs/2_architecture/system_design.md`
- Active work: `dev/active/`
