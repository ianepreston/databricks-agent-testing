---
name: deploy
description: "Deploy this repo's bundle and its Databricks Apps (e.g. agent-calendar-v1). Use when: (1) User says 'deploy', 'redeploy', 'push to databricks', or 'bundle deploy', (2) 'App already exists' error occurs, (3) Need to bind/unbind an existing app, (4) Debugging or querying a deployed app."
---

# Deploy the bundle

The bundle root is the repo root (`databricks.yml`). App definitions live in
`resources/<app>.app.yml`. Run every command below from the repo root, with the
profile from `.env`:

```bash
P="$DATABRICKS_CONFIG_PROFILE"   # loaded by direnv from the root .env
```

| App | Bundle resource key | Definition |
|-----|---------------------|------------|
| `agent-calendar-v1` | `agent_calendar_v1` | `resources/agent-calendar-v1.app.yml` |

## Deploy and restart

```bash
task check                                  # local preflight + unit tests
task bundle:validate                        # strict validation
databricks bundle plan -t dev --profile "$P"   # review: look for delete/recreate
databricks bundle deploy -t dev --profile "$P"
databricks bundle run agent_calendar_v1 -t dev --profile "$P"
```

`bundle deploy` uploads source and updates resources but does **not** restart
the app with new code. `bundle run <key>` is required afterwards.

The deploy applies every resource in the bundle (catalog, model service,
experiment, apps), not just the app you changed — check the plan.

## Verify the deployed app

Apps accept OAuth tokens only (a PAT returns a 302 redirect).

```bash
URL=$(databricks apps get agent-calendar-v1 --profile "$P" -o json | jq -r .url)
TOKEN=$(databricks auth token --profile "$P" | jq -r .access_token)
curl -sf -H "Authorization: Bearer $TOKEN" "$URL/health"
curl -s -X POST "$URL/api/chat" -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"message":"What is today? Return only the ISO date."}'
```

## Debug

```bash
databricks apps get agent-calendar-v1 --profile "$P" -o json | jq '{app_status, compute_status, active_deployment}'
databricks apps logs agent-calendar-v1 --profile "$P"    # requires OAuth (U2M) auth
```

| Issue | Fix |
|-------|-----|
| App runs old code after deploy | `databricks bundle run <key>` |
| Runtime permission error on a tool/resource | Add the grant under `resources:` in `resources/<app>.app.yml` (see the app's **add-tools** skill), redeploy |
| `BUNDLE_VAR_catalog_storage_root` unset | Set it in the root `.env`, then `direnv allow` |
| "Provider produced inconsistent result" | Sync server-side app settings (e.g. `budget_policy_id`) into `resources/<app>.app.yml` |

## "An app with the same name already exists"

Ask the user whether to bind the existing app or delete and recreate it.

- **Bind:** copy server-side settings from
  `databricks apps get <name> --profile "$P" -o json` into the app's resource
  file, confirm it isn't already bound (`databricks bundle summary -t dev --profile "$P" -o json | jq .resources.apps`),
  then `databricks bundle deployment bind <key> <name> -t dev --profile "$P"`,
  then deploy.
- **Delete:** `databricks apps delete <name>` permanently removes the app's URL,
  OAuth client, and service principal. Only with explicit user approval.

`databricks bundle deployment unbind <key>` detaches without deleting.

## Notes

- Changing an app's `name` forces delete + recreate (new URL and service principal).
- New agent apps use the `agent-*` name prefix unless told otherwise.
- CI: `.github/workflows/deploy.yml` (manual trigger; needs a `prod` target, see its header).
