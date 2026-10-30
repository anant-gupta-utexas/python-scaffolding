# python-scaffolding

A [Copier](https://copier.readthedocs.io) template for Python projects. One command gives you a
working repo with the directory structure, planning workflow, uv setup and quality gate that
I use everywhere, in the flavor that fits the project.

```bash
uvx copier copy --trust gh:anant-gupta-utexas/python-scaffolding my-new-project
cd my-new-project
scripts/check.sh          # passes on a fresh checkout
```

`--trust` is needed because the template runs three post-generation tasks: `git init`, `uv sync`,
and (data science only) `nbstripout --install`. Nothing is committed for you.

## Flavors

| Flavor | You get |
|---|---|
| `library_cli` | `argparse` entry point (`cli.py`, `python -m`, `[project.scripts]`) |
| `service` | FastAPI + Clean Architecture (`domain/application/infrastructure`), `pydantic-settings`, domain-error to HTTP mapping, Dockerfile, compose, `.env.example` |
| `datascience` | `ingest/features/models`, gitignored `data/` with a `paths` helper, `notebooks/` with `nbstripout`, pandas/duckdb/pyarrow |

Every flavor also gets:

- **uv + src layout**, hatchling, `.python-version`
- **`scripts/check.sh`**, the one quality gate (ruff lint + format, `mypy --strict`, size limits of
  400 warn / 800 max per file and 50 per function, secret scan, pytest with a coverage floor).
  CI runs the same script
- **`AGENTS.md`** (with `CLAUDE.md` importing it) and **`STATUS.md`**
- **`docs/00_research … 04_testing`** with an index, and **`dev/active|archive`** with
  plan/context/tasks templates; `scripts/new_feature.sh <name>` scaffolds a feature's planning docs

## Questions

| Question | Default | Effect |
|---|---|---|
| `project_name` | My Project | Titles, docs |
| `package_name` | derived from the name | `src/<package_name>/`, distribution name |
| `description` | placeholder | `pyproject.toml`, README |
| `flavor` | `library_cli` | Which files and dependencies you get |
| `python_version` | 3.13 | `.python-version`, ruff, mypy, Docker image |
| `min_coverage` | 80 | Coverage floor enforced by the gate |

Answers are saved in `.copier-answers.yml`; non-interactive use: `--defaults --data flavor=service`.

## Updating a project when the template improves

```bash
cd my-project && git status          # must be clean
uvx copier update --trust
```

Copier does a three-way merge between the old template, the new template and your edits. Releases
are git tags (`v0.1.0`, `v0.2.0`, ...): tag the template when you want projects to pick up a change.

## Developing the template

```bash
uv sync
uv run pytest                  # everything; the gate tests run `uv sync` per flavor (needs network)
uv run pytest -m "not gate"    # fast: structure, rendering, validation, copier update
```

The suite generates every flavor, asserts each gets only its own files, checks that no Jinja is left
unrendered, exercises validation and `copier update`, and runs each generated project's own
`scripts/check.sh`. See [`AGENTS.md`](AGENTS.md) for how the template is organized and the rules for
changing it.

## License

MIT, see [`LICENSE`](LICENSE).
