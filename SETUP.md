# Install Weft

This guide takes you from a clean copy of Weft to a working connection through Make MCP.

The installer creates and configures the Make resources. Before running it, you duplicate the Notion template and connect Notion and Make. After installation, you connect Weft to your MCP client and test it with a short conversation.

Most of the work happens through the installer. The manual steps are included where they are needed.

## Before you start

You need:

- Git, or a way to download and extract a GitHub ZIP;
- Python 3.13.3, which is the tested runtime;
- a Notion account and workspace;
- a Make account and target team;
- ChatGPT or Claude for the final MCP test.

Windows is the live-tested installation platform. The installer path has also been tested in WSL. macOS and Linux commands are included, but macOS has not been live-tested and broader Python-version support has not been established.

The external services used in this guide are:

```text
https://www.notion.so/
https://www.make.com/
https://chatgpt.com/
https://claude.ai/
https://mcp.make.com
```

## Prepare the repository and Python environment

Clone the repository:

```powershell
git clone https://github.com/nadira-busse/weft.git Weft
cd .\Weft
```

Downloading the ZIP from `https://github.com/nadira-busse/weft` is also supported. Extract it to a new directory and run the remaining commands from that repository root.

Create the tested Windows environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
python -m installer --help
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, create and activate the environment with:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip check
python3 -m installer --help
```

The help output should list `configure`, `preflight` and `install`. Keep the environment active for the rest of the guide.

Create the private configuration file:

```powershell
Copy-Item .env.example .env
```

On macOS or Linux:

```bash
cp .env.example .env
```

Keep `.env` out of Git. The installer also creates `.weft-installer/` for local target IDs, generated files and recovery information. Keep both private.

## Duplicate and authorize Notion

Open the [Weft Notion template](https://weft-template.notion.site/Weft-3ae38e363cc580f8b137e96d8e6633fa).

Click **Duplicate**, choose the target workspace and wait for the page to finish copying. You should now see:

- Archive
- Projects
- Daily Log
- Error Logs

Archive relates to Projects and Daily Log. Projects and Daily Log each receive their reciprocal Archive relation; the Daily Log `Projects` field is a rollup, not a direct relation. Do not rebuild these properties manually during a normal installation.

If a relation is disconnected or still points to the source workspace, follow the repair steps in the [Notion database schema](./setup/notion/database-schema.md).

Create a Notion internal integration from the duplicated Weft page through **Connections → Developer portal → New connection**. Give it a recognizable name, copy its access token and grant at least:

- read content;
- update content;
- insert content;
- read user information, including email addresses.

Under **Content access**, add the duplicated Weft page and confirm that all four databases are included. Store the token only in `.env`:

```dotenv
NOTION_INSPECT_TOKEN="<notion-token>"
```

The installer uses this token only for Notion search and GET requests. The write permissions are needed by the Make Notion connection when the installed workflows later create or update records.

## Prepare the Make team and connections

Log in at `https://www.make.com/` and select the organization and team where you want to install Weft. An empty team, or one without another Weft installation, gives you the cleanest starting point. The installer discovers the organization and team IDs later.

Read the zone from the beginning of the Make URL and add only its identifier to `.env`:

```text
https://eu1.make.com/  →  MAKE_ZONE="eu1"
https://eu2.make.com/  →  MAKE_ZONE="eu2"
https://us1.make.com/  →  MAKE_ZONE="us1"
```

Create one Make API token under **Profile → API Access** with these permissions:

- Connections: Read
- Organizations: Read
- Scenarios: Read and Write
- Teams: Read
- User Defined Types: Read and Write

Store it only in `.env`:

```dotenv
MAKE_API_TOKEN="<make-token>"
```

The installer binds workflows only to connections already present in the target team. Create both connections in one temporary Make scenario.

For Notion:

1. Add **Notion → Create a Data Source Item**.
2. Create a **Notion Internal** connection, for example `weft-make-notion-connection`.
3. Paste the same Notion token stored in `NOTION_INSPECT_TOKEN`.
4. Use **ID finder** to select the duplicated Archive database.
5. Enter a temporary title, save the module and choose **Save anyway** if Make says the temporary scenario is incomplete.

For Make AI:

1. Add **Make AI Toolkit → Simple Text Prompt** to the temporary scenario.
2. Create a connection, for example `weft-ai-connection`.
3. Select **Small** as the model, enter temporary text and save the module.

Create the AI connection in Make itself so that it is visible and available to the installer. Preflight also checks this connection because it is used by the optional `create_daily_log` scenario.

Confirm both connections under **Credentials → Connections**. Keep the temporary scenario until installation and connection verification are complete.

## Configure the local target

Your `.env` should now contain:

```dotenv
MAKE_ZONE="your-zone"
MAKE_API_TOKEN="<make-token>"
NOTION_INSPECT_TOKEN="<notion-token>"
```

Run:

```powershell
python -m installer configure
```

Use `python3` instead of `python` on macOS or Linux.

`configure` reads accessible Make organizations and teams. It selects automatically when only one valid choice exists and asks you to choose by name when several exist. It then writes these non-secret values to `.env`:

```dotenv
MAKE_API_BASE_URL="https://your-zone.make.com/api/v2"
MAKE_ORGANIZATION_ID="discovered-id"
MAKE_TEAM_ID="discovered-id"
```

The result should show `status: CONFIGURED`, `secrets_written: false` and the organization and team you selected.

Leave `WEFT_NOTION_CONNECTION_ID` and `WEFT_AI_CONNECTION_ID` empty when each connection family has one valid target-team match. If preflight finds several, use the candidate ID for the intended connection. IDs are hidden from normal terminal output; a local diagnostic run can show them with:

```powershell
python -m installer preflight --show-ids
```

Treat that output as private. `WEFT_INSTALLATION_NAME` and `WEFT_STATE_FILE` are also optional. A custom state path must remain below `.weft-installer/`.

## Know what each command changes

| Step | Local effect | Make | Notion |
|---|---|---|---|
| `configure` | Updates non-secret target fields in `.env`. | Reads organizations and teams. | No request. |
| `preflight` | Writes full and sanitized reports under `.weft-installer/`. | Reads authorization, target resources and connections. | Searches and reads the four databases. |
| `install` | Writes state, generated candidates and reports under `.weft-installer/`. | Creates or reuses Data Structures, creates scenarios and may stop a state-owned scenario to restore the inactive end state. | Read-only discovery; no direct Notion write. |
| Runtime acceptance | No installer write. | You manually activate scenarios; the scenarios execute. | The archive test creates or updates sanitized test records. |

Notion duplication, integration creation, Make connection creation, scenario descriptions, activation and MCP authorization are manual platform changes outside the installer.

## Run the read-only preflight

Run:

```powershell
python -m installer preflight
```

Preflight checks:

- the Make token scopes and the configured team/organization pair;
- the five exported blueprints and four Data Structure contracts;
- access to Archive, Projects, Daily Log and Error Logs and their required properties;
- one valid target-team Notion connection and one UI-visible, scoped `ai-provider` connection;
- existing scenario and Data Structure names;
- every connection, Data Structure, Notion resource/property and child-scenario replacement;
- the dependency from `get_context` to the newly installed `notion_text_formatter`.

It builds future candidates with temporary IDs in memory and performs zero external mutations. It does write these local reports:

```text
.weft-installer/preflight-report.json
.weft-installer/preflight-report.sanitized.json
```

A successful compact result shows:

- `status: PREFLIGHT_PASSED`;
- the intended organization and team;
- four Notion databases found;
- four Data Structures planned;
- five scenarios planned;
- `performed_make_mutations: 0`;
- `performed_notion_mutations: 0`.

If preflight stops, follow the reported action and run it again before continuing to `install`.

## Create the Make resources

Run:

```powershell
python -m installer install
```

`install` runs preflight again before its first provisioning write.

The four Data Structures are runtime resources used by Make's JSON modules; they are separate from the JSON Schemas in `schemas/` and from scenario input/output definitions:

- `Weft - Archive Messages` shapes the normalized message array for archiving.
- `Weft - Search Archive Response` shapes the search result array.
- `Weft - Get Context Response` shapes full-content results and their numeric metadata.
- `Weft - Daily Log Content` parses the AI result used by optional `create_daily_log`.

On a fresh team, the installer creates these Data Structures and records their IDs. On a rerun, it can reuse resources recorded in its local state. If it finds duplicate or incompatible matches, it stops instead of choosing one for you.

The installer creates these scenarios:

- `notion_text_formatter` — internal child workflow;
- `archive_conversation` — MCP-exposed workflow;
- `search_archive` — MCP-exposed workflow;
- `create_daily_log` — optional supporting workflow;
- `get_context` — MCP-exposed workflow that calls the new formatter scenario.

The installer replaces the source connection IDs, Data Structure IDs, Notion bindings and scenario references with the values from your Make and Notion environment. The exported files remain unchanged under:

```text
setup/Make/blueprints/
```

Each scenario uses on-demand scheduling and remains inactive. The installer then reads it back from Make to check that it was stored in the selected team with the expected configuration. It does not run the scenarios.

Successful installation ends with:

```text
LOCALLY_VERIFIED_CLEAN_INSTALL_PENDING
```

This means the resources were created and read back successfully. The short MCP test later in this guide checks the runtime behavior.

Local recovery material is written below `.weft-installer/`, including:

```text
installation-state.json
installation-report.json
installation-report.sanitized.json
installation-error.json
installation-error.sanitized.json
candidates/
```

If installation stops, keep `.weft-installer/` and the inactive Make resources in place. The reports record what was created and whether it is safe to retry. When an error shows `retry_safe: false`, review that error before running `install` again.

The installer does not delete resources or roll changes back automatically. You should not need to repair individual blueprint modules by hand.

## Finish the Make setup

Open the selected Make team and check that the four Data Structures and five scenarios are present. The scenarios should all be inactive at this point.

Make does not import scenario descriptions from these blueprints. Add the following descriptions in Make without changing inputs, outputs, mappings or scheduling:

- `archive_conversation`: `Archives a conversation to Notion. Use only on explicit archive request. Store input exactly as given. Do not generate or convert timestamps. Required: conversation_id, title, project, extraction_type, messages, start_time.`
- `search_archive`: `Searches the Weft Notion archive for stored conversations using a title, keyword, project, date, category, or other available search criteria. Returns matching archive records and their identifying metadata.`
- `get_context`: `Retrieves stored conversation content from Archive records matching a conversation ID, project, exact date or text query. Use this when the archived content itself is needed rather than search metadata.`
- `notion_text_formatter`: `Internal helper scenario that converts Notion archive content into a normalized text format for context retrieval. This scenario is called by get_context and is not intended for direct use by MCP clients.`
- `create_daily_log`: `Creates or updates the Daily Log in Notion by combining the current day’s work-session summaries, generating a concise AI summary, extracting follow-up actions, and storing the result.`

The supplied workflows use `Europe/Amsterdam` for `weft_timezone`. If your installation uses another timezone, change `weft_timezone` and use the same IANA timezone in `archive_conversation`, `search_archive` and, when used, `create_daily_log`.

Check that the Notion and AI modules use the connections you created. You can then remove the temporary scenario. Leave `create_daily_log` inactive unless you want to use that optional workflow.

## Connect Make MCP

Expose only these scenarios to clients through MCP:

- `archive_conversation`
- `search_archive`
- `get_context`

`notion_text_formatter` is called only by `get_context`; `create_daily_log` is not exposed through the MCP interface.

For ChatGPT, open **Settings → Plugins → Developer mode**, add a plugin and use:

```text
Name: Weft
Description: Weft environment for archiving conversations, searching archives, and retrieving stored context through Make and Notion.
Connection: https://mcp.make.com
Authentication: OAuth
```

Authorize the correct Make organization and select:

```text
Execute any active and on-demand scenarios using MCP
```

For Claude, open **Settings → Connectors → Add → Add custom connector**, enter a recognizable name and use:

```text
https://mcp.make.com
```

Authorize the same Make organization and select the same active/on-demand permission. Claude cannot add the same remote MCP URL twice; reuse or remove an existing connector when needed. Do not store client authorization tokens in this repository.

Refresh the ChatGPT plugin or Claude connector whenever you change which Make scenarios are active.

## Test the setup

Use sanitized content and one new conversation ID throughout, for example:

```text
weft-install-test-YYYYMMDD-HHMM
```

Provide the actual start time rather than copying a placeholder.

The Make Free plan tested on 19 August 2026 allowed two active scenarios at a time. The steps below account for that by using two short rounds.

1. Activate `archive_conversation` and `search_archive`; keep the other scenarios inactive.
2. Through ChatGPT, archive a short sanitized conversation with the new ID, a title, project, `extraction_type: conversation` and the actual `start_time`.
3. Confirm the Archive record and full content in the duplicated Notion workspace.
4. Search by the same `conversation_id` and confirm the returned ID and metadata.
5. Deactivate `archive_conversation` and `search_archive`.
6. Activate `get_context` and `notion_text_formatter`, then refresh the client connection.
7. Through Claude, retrieve the stored content using the same ID.
8. If you want to repeat the full clean-account test, run archive, search and retrieval through both clients.
9. Return all installer-created scenarios to inactive after testing unless ongoing activation was separately intended.

One known Make MCP issue can reject an archive request containing a Markdown-formatted `python -m ...` command with HTTP 403 before the scenario starts. The reproduced diagnosis, workaround and other current boundaries are documented in [known limitations](./setup/known-limitations.md).

Your setup should now contain four related Notion databases, four Make Data Structures and five Make scenarios. Three scenarios are available through MCP: `archive_conversation`, `search_archive` and `get_context`.

Weft is ready when the test conversation appears in Notion, `search_archive` finds it and `get_context` returns its stored content.

The full setup was tested on Windows on 19 August 2026. Repeat the relevant runtime checks after a blueprint or runtime behavior changes.
