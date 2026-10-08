# agent-calendar-v1 — app guide

App source for the `agent-calendar-v1` Databricks App. This folder is the
app's `source_code_path`: everything here is uploaded as-is. The runtime
command and env are set in the `config:` block of
`../resources/agent-calendar-v1.app.yml`.
Repo-level conventions, commands, and deployment live one level up — read
`../AGENTS.md` and `../.claude/skills/deploy/SKILL.md`.

## What this app is

A deliberately small, stateless FastAPI chat app built with the OpenAI Agents
SDK (see `README.md`):

- `GET /` bare chat page, `GET /health`, `POST /api/chat` (`{"message": ...}`).
- Model: Unity Gateway model service `databricks_agent_testing.default.demo_model`
  (defined in `../resources/model-service.yml`).
- Tools: local `get_current_date`, plus Google Calendar MCP restricted to
  `calendar_event_list`.
- Auth: deployed requests use the signed-in user's forwarded token
  (`user_api_scopes: [ai-gateway]`); locally, `DATABRICKS_CONFIG_PROFILE`.
- No MLflow tracing, no memory, no conversation history.

## Key files

| File | Purpose |
|------|---------|
| `agent_server/agent.py` | Model client, tools, MCP server, agent instructions |
| `agent_server/app.py` | FastAPI routes and the chat page |
| `agent_server/start_server.py` | Uvicorn entry point (`uv run start-server`) |
| `../resources/agent-calendar-v1.app.yml` | Bundle definition: runtime command/env, scopes, resource grants |
| `scripts/preflight.py` | Local smoke test used by `task preflight` |
| `tests/` | Unit tests (`task test`) |

## Template skills in `.claude/skills/`

The remaining skills come from the Databricks "OpenAI Agents SDK" agent
template and describe *that* template (MLflow `AgentServer`, `/invocations`,
`databricks_openai`). Use them for patterns, then translate to this repo:

- "Edit `databricks.yml`" / resource key `agent_openai_agents_sdk` → edit
  `../resources/agent-calendar-v1.app.yml`, key `agent_calendar_v1`.
- `uv run start-app` / `/invocations` → `task run` / `POST /api/chat`.
- "Set it in `app.yaml`" (env vars, command, OAuth scopes) → the app resource's
  `config:` block or `user_api_scopes` in `../resources/agent-calendar-v1.app.yml`.
- Run bundle commands from the repo root, not this folder.

| Task | Skill |
|------|-------|
| Find workspace tools/resources | **discover-tools** |
| Create tool resources (Genie, Vector Search, UC functions) | **create-tools** |
| Add tools and grant app permissions | **add-tools** |
| Change agent code, model, or instructions | **modify-agent** |
| Cross-session memory | **managed-memory** |
| Server-side agent loop | **supervisor-api**, **supervisor-api-background-mode**, **supervisor-api-client-function-calling** |
| Long-running tasks | **long-running-server** |
| Load testing | **load-testing** |

When adding a tool that touches a Databricks resource, also add the matching
grant under `resources:` in `../resources/agent-calendar-v1.app.yml`.
