# Connection and Binding Reference

The canonical connection-authorization and MCP setup sequence is [`../SETUP.md`](../SETUP.md). This reference records the connection families, scopes, dependency bindings, and exposure boundary that the installer verifies.

Blueprint connection labels and IDs such as `notion3`, `ai-provider`, and `SCN_...` are environment-specific bindings, not credentials. The installer discovers and replaces them structurally; users do not relink every module.

## Make API token

The required `MAKE_API_TOKEN` scope set is:

- `connections:read`
- `organizations:read`
- `scenarios:read`
- `scenarios:write`
- `teams:read`
- `udts:read`
- `udts:write`

`configure` derives the API base URL from `MAKE_ZONE`, discovers the accessible organization and team, asks for a readable choice when needed, and writes `MAKE_API_BASE_URL`, `MAKE_ORGANIZATION_ID`, and `MAKE_TEAM_ID` to the local `.env`.

## Notion inspection and Make connection

`NOTION_INSPECT_TOKEN` is a Notion integration token used by the installer only for search and GET requests. Share `Archive`, `Projects`, `Daily Log`, and `Error Logs` with this integration.

Separately, authorize one Make Notion connection for the duplicated workspace and grant it access to the same resources. The installer selects a unique target-team connection whose family is `notion3`. When multiple matches exist, set `WEFT_NOTION_CONNECTION_ID`; the explicit connection must still pass family and target checks.

The installer discovers the four data sources through the Notion API, matches required property names, and replaces Notion bindings at structural paths using the target property IDs and exported target types where required by Make. It never writes to Notion during preflight or installation.

## AI-provider connection

Only optional `create_daily_log` uses the AI connection. Make’s API-created connection did not satisfy the proven UI-visible boundary, so the connection must be created and authorized through an AI Toolkit module as documented in [`../SETUP.md`](../SETUP.md).

Preflight requires exactly one target-team record with family `ai-provider`, account type `basic`, and scoped authorization. Use `WEFT_AI_CONNECTION_ID` only to disambiguate multiple valid records. The installer binds module 43 while preserving provider family `ai-provider` and model `small`.

## Scenario dependencies

The installer creates `notion_text_formatter` before `get_context`, captures the returned ID, and binds every exported formatter reference to `SCN_<new-id>`. No scenario ID is copied from configuration or manually entered in a module.

## MCP exposure

After installation and runtime verification, expose only:

- `archive_conversation`
- `search_archive`
- `get_context`

`notion_text_formatter` is an internal child. `create_daily_log` is an optional supporting workflow, not a public MCP contract. Configure MCP endpoints and authorization in ChatGPT and Claude without storing client tokens in this repository.

## Recorded acceptance status

| Evidence context | Status | Meaning |
|---|---|---|
| Owner’s existing ChatGPT environment | Prior manual runtime acceptance: passed | All public MCP scenarios and established regression routes passed |
| Owner’s existing Claude environment | Prior manual runtime acceptance: passed | MCP connection and all public scenarios passed |
| Previously tested installer environment | `FUNCTIONALLY_PASSED_WITH_RESIDUAL` | Automated provisioning/read-back/runtime path passed with the UI connection residual |
| Full public installer flow in new Notion, Make, ChatGPT, and Claude accounts | Passed on 6 August 2026 | Clean provisioning and client acceptance completed for the tested release |
| `archive_conversation` V4 Routes 1–7 | Expected MCP/Make responses and all defined manual assertions confirmed on 6 August 2026 | [Canonical V4 report](../regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md); confirmation is limited to the persistence, side-effect, and precondition assertions defined by the procedure |
| Modified canonical blueprint after this synchronization | Pending | Requires fresh provisioning and live Route 1–7, Notion, ChatGPT, and Claude verification for the published canonical revision |

The public installer does not rerun external client tests.
