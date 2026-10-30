---
project: "python-scaffolding"
status: building           # design | building | shipped | maintenance | paused
phase: "v0.1.0: Copier template released"
last_updated: 2026-10-30
next_gate: "Fork into an org-specific template with a toggle (step 2)"
blocked_on: null           # short string, or null
---

# python-scaffolding: status

## Current

A Copier template with three flavors (`library_cli`, `service`, `datascience`). It generates a
project with the standard structure (docs, dev planning, one quality gate) and `copier update`
support. v0.1.0 is merged to `main` and tagged. The test suite generates every flavor and runs
its own gate.

## Recent (last 7 days)

- Converted the old Clean Architecture scaffold into a Copier template.
- Added the test suite: flavor file selection, rendering, validation, `copier update`, and a gate
  run per flavor.
- Merged to `main` and tagged `v0.1.0`.

## Next

- Fork the repo into a separate remote and add the org-specific toggle there.
- Build the service Dockerfile once Docker is available (it has not been built yet).

## Blocked / waiting

- 

## Pointers

- Usage: `README.md`
- Maintainer rules: `AGENTS.md`
- Template source: `copier.yml`, `template/`
- Tests: `tests/test_template.py`
