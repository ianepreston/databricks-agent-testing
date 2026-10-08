# databricks-agent-testing

A single Declarative Automation Bundle (`databricks_agent_testing`) that manages
shared Databricks resources plus one or more agent apps.

## Layout

| Path | Purpose |
|------|---------|
| `databricks.yml` | The only bundle root. Targets, variables, and `include: resources/*.yml`. |
| `resources/` | One file per resource. Every app's permissions, env, and resource grants live here. |
| `resources/catalog.yml` | `databricks_agent_testing` catalog (needs `BUNDLE_VAR_catalog_storage_root`). |
| `resources/model-service.yml` | Unity Gateway model service `databricks_agent_testing.default.demo_model`. |
| `resources/agent-calendar-v1.*.yml` | The calendar app and its MLflow experiment. |
| `agent-calendar-v1/` | App source only. Uploaded as the app's `source_code_path`; has its own `pyproject.toml`/`uv.lock`. See its `AGENTS.md`. |
| `Taskfile.yaml` | Development loop (`task --list`). |
| `.github/workflows/` | CI. GitHub only reads workflows from the repo root. |

Each app lives in its own subdirectory because an app's `source_code_path` is
uploaded as-is and must have `pyproject.toml` and `uv.lock` at its root. Keep
everything else (bundle config, CI, repo docs, deploy skills) here.

## Conventions

- Run all `databricks bundle` commands from the repo root.
- All app configuration lives in `resources/<app>.app.yml`: the runtime
  `command` and `env` in its `config:` block, plus scopes, permissions, and
  resource grants (`source_code_path` there is relative to `resources/`). App
  folders hold source code only. When template docs say to edit
  `databricks.yml` or `app.yaml`, edit this file.
- Bundle resource keys use underscores (`agent_calendar_v1`); app names use
  hyphens (`agent-calendar-v1`).
- `direnv` loads the ignored root `.env` (see `.env.example`), which sets
  `DATABRICKS_CONFIG_PROFILE` and `BUNDLE_VAR_catalog_storage_root`. Always pass
  `--profile "$DATABRICKS_CONFIG_PROFILE"` to the CLI.

## Commands

```bash
task sync             # install the app's locked dependencies
task run              # run the app locally at http://localhost:8000
task test             # unit tests
task preflight        # start the app, check /health and one chat request
task bundle:validate  # strict bundle validation
```

Deploying: see `.claude/skills/deploy/SKILL.md`.
