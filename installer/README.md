# Weft public installer

The public installer provisions and verifies the Make resources required by Weft.

## Commands

```powershell
python -m installer configure
python -m installer preflight
python -m installer install
```

### `configure`

`configure` is a local configuration step. The user first copies `.env.example` to `.env` and manually enters:

- `MAKE_ZONE`;
- `MAKE_API_TOKEN`;
- `NOTION_INSPECT_TOKEN`.

The command uses the Make token to discover accessible organizations and teams. When one valid target exists, it is selected automatically. When several exist, the user selects one by name. The command writes only these non-secret values to `.env`:

- `MAKE_API_BASE_URL`;
- `MAKE_ORGANIZATION_ID`;
- `MAKE_TEAM_ID`.

It does not create or change Make or Notion resources. It does not write, print, or report token values.

### `preflight`

`preflight` is read-only. It validates configuration, token scopes, the selected organization/team boundary, canonical blueprints, Data Structure contracts, Notion resources, Make connections, dependency replacements, and existing target resources. The terminal shows a compact summary; the complete sanitized report is written to `.weft-installer/preflight-report.sanitized.json`.

### `install`

`install` creates or safely reuses four Data Structures and creates five inactive scenarios. It records new IDs, applies target bindings, verifies read-back, and stores private state under `.weft-installer/`.

## Required private values

Create one Make API token with:

- `connections:read`
- `organizations:read`
- `scenarios:read`
- `scenarios:write`
- `teams:read`
- `udts:read`
- `udts:write`

Create one Notion internal integration token with access to the duplicated Weft page and its four core databases.

Never commit `.env` or `.weft-installer/`.
