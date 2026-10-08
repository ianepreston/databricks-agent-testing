# Calendar Assistant

A deliberately small Databricks App for learning agent implementation. It is a
FastAPI service with a bare browser chat page, built with the OpenAI Agents SDK
and deployed directly as a Databricks App.

## What is implemented

- A browser chat page at `/`, plus `GET /health` and `POST /api/chat`.
- A stateless, one-turn agent: it keeps no conversation history or durable
  cross-session state.
- Unity Gateway inference through the UC model service
  `databricks_agent_testing.default.demo_model`.
- A local `get_current_date` function tool.
- Read-only Google Calendar MCP access, limited to `calendar_event_list`.
- Local authentication through `DATABRICKS_CONFIG_PROFILE`; deployed requests
  use the signed-in App user's forwarded access token.
- No MLflow tracing requirement or tracing configuration.

## Local development

This repository uses `direnv` to load the ignored root `.env`, including
`DATABRICKS_CONFIG_PROFILE`. Once after cloning (and whenever `.envrc` changes):

```bash
direnv allow
echo "$DATABRICKS_CONFIG_PROFILE"
```

From the repository root, `task` provides the normal development loop:

```bash
task                 # discover commands and descriptions
task sync            # install the lockfile's dependencies
task run             # start the app at http://localhost:8000
task preflight       # test /health and one local chat request
task test            # run the automated tests
task check           # preflight and tests
task bundle:validate # strict bundle validation; needs BUNDLE_VAR_catalog_storage_root
```

With `task run` active, use the page at http://localhost:8000 or call the
minimal API directly:

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is today? Return only the ISO date."}'
```

## Dependency registries

Local `uv` configuration may use the Databricks package proxy. The committed
`uv.lock` and the deployed App use public PyPI (`pypi.org` and
`files.pythonhosted.org`) instead. Do not regenerate the committed lockfile
through a local-only proxy.

## Deployed app

The development app is available at
https://agent-calendar-v1-7405618287403507.7.azure.databricksapps.com.

Deployment configuration lives in `../resources/agent-calendar-v1.app.yml`.
