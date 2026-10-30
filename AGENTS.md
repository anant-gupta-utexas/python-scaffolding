# python-scaffolding: maintainer guide

This repo is a Copier template, not an application. Everything a generated project contains lives
in `template/`; `copier.yml` holds the questions and the file-selection rules; `tests/` proves
every flavor works. User-facing docs are in `README.md`.

## Layout

```
copier.yml            # questions, derived flags (is_cli / is_service / is_ds), _exclude, _tasks
template/             # the generated project (Jinja where a file has a .jinja suffix)
tests/test_template.py
pyproject.toml        # dev tools only (copier, pytest, ruff); package = false
```

## How flavors work

Files are plain directories under `template/`. `copier.yml` `_exclude` renders Jinja and matches
the **rendered destination path**, so `{% if not is_service %}src/{{ package_name }}/domain{% endif %}`
drops the folder for other flavors (an empty pattern excludes nothing). To add or move a
flavor-specific file, add it normally and add its exclusion line. To add a flavor: a new `choices`
entry, an `is_<flavor>` flag, exclusions, dependencies in `pyproject.toml.jinja`, docs
conditionals, and entries in `FLAVOR_ONLY` and `FLAVORS` in the tests.

## Rules

- **Every flavor must pass its own `scripts/check.sh` untouched.** `pytest -m gate` proves it; do
  not merge with it red. Run the whole suite before every commit.
- **Stay organization-neutral.** No company names, internal mirrors or internal tooling. A test
  fails the build if banned words appear. Org-specific variants are forks of this repo.
- **Use `.jinja` only when a file needs it.** Static files are copied verbatim. Generated Python
  must be stable under `ruff format` for any project name or description (use magic trailing
  commas and `| tojson` for user text; keep user text out of docstrings).
- **Derived values stay hidden** (`when: false`): they are recomputed on `copier update`, never
  stored in the answers file.
- **Tasks must be idempotent**: they run on `copy` and on `update`.
- **DRY.** One `check.sh`, one `check_sizes.py`: parameterize through `pyproject.toml`, do not fork
  per flavor. Keep docs stubs short and prompt-like; long boilerplate becomes a lie.
- **No lockfile here**: `uv.lock` is gitignored on purpose (its index URLs depend on who ran it).
- Follow the limits we enforce on generated projects: files < 400 lines (800 max), functions < 50.
- Releases are git tags (`vX.Y.Z`); `copier update` in downstream projects follows them.

## Verifying a change by hand

```bash
uvx copier copy --trust --defaults --data flavor=service . /tmp/demo
cd /tmp/demo && scripts/check.sh
```
