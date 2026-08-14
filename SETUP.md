# Install Weft

> Last live-tested: 6 August 2026.
>
> The complete clean-install and acceptance flow was successfully completed with new free Notion, Make, ChatGPT, and Claude accounts. Product interfaces, labels, plan limits, and availability may change after this date.
>
> The `archive_conversation` V4 regression run produced the expected MCP/Make responses, and all manual assertions defined by the test procedure were verified and confirmed for all seven route classes on 6 August 2026. The [V4 regression report](./regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md) records the exact assertions covered; it does not claim inspection of every theoretically possible side effect.
>
> Canonical synchronization after that acceptance requires fresh post-change provisioning and live verification. Repository tests do not replace that step.

This guide takes a first-time user from the public GitHub repository to a working Weft installation connected through Make MCP.

You do not need an existing Weft installation, `.env`, Python virtual environment, or `.weft-installer` state.

You also do not need to find internal Make organization or team IDs yourself. The installer discovers them and writes only the required non-secret values to your local `.env` file.

## Installation flow

1. Clone or download the repository.
2. Create the Python virtual environment and install dependencies.
3. Create the local `.env` file.
4. Duplicate and connect Notion.
5. Prepare Make and create the required connections.
6. Run `configure`.
7. Run the read-only `preflight`.
8. Run `install`.
9. Verify the created Make resources.
10. Add the scenario descriptions.
11. Activate the scenarios required for the current test round.
12. Connect ChatGPT and Claude to the Make MCP Server.
13. Run the end-to-end acceptance tests.

---

## 1. What you need

Before starting, make sure you have:

- a Git client, or the ability to download and extract a GitHub repository ZIP;
- a Notion account;
- a Make account;
- Python 3.13.3, the tested runtime version;
- ChatGPT or Claude for the MCP acceptance test.

Broader Python-version compatibility is not claimed.

### Free-plan use

The full installation and acceptance flow was successfully tested with free accounts on 6 August 2026.

Weft contains five Make scenarios. On the Make Free plan, no more than two scenarios can be active at the same time. This does not block installation because the installer leaves all five scenarios inactive.

A scenario can be configured as **On demand** while remaining inactive. During testing, activate only the scenarios required for the current test round.

For regular use without repeatedly activating and deactivating scenarios, a suitable paid Make plan is more practical.

### Platform status

- Windows: live clean-install tested.
- macOS: commands documented, not yet live tested.
- Linux: commands documented, not yet live tested.

---

## 2. Get a clean local copy of Weft

For the strongest first-time-user path, clone the public GitHub repository into a new local folder.

On the GitHub repository page:

1. Click **Code**.
2. Copy the HTTPS clone URL.
3. Open a terminal in the parent directory where you want to store Weft.

### Windows PowerShell

```powershell
git clone https://github.com/nadira-busse/weft.git Weft
cd .\Weft
```

### macOS or Linux

```bash
git clone https://github.com/nadira-busse/weft.git Weft
cd Weft
```

You can confirm the checked-out revision with:

```bash
git rev-parse HEAD
```

Keep this commit SHA when you are performing release or reproducibility acceptance for a specific repository revision.

### Alternative: Download ZIP

If Git is not available, GitHub's **Download ZIP** option can be used instead.

Extract the ZIP to a new folder and open a terminal in the repository root.

Do not reuse:

* an existing `.env`;
* an existing `.venv`;
* an existing `.weft-installer` directory;
* installer candidates or reports from another installation.

---

## 3. Create the Python environment

Create a new virtual environment inside the repository and install the public dependencies.

### Windows PowerShell

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

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip check
python3 -m installer --help
```

Expected:

* no broken requirements;
* installer help lists `configure`, `preflight`, and `install`.

Keep the virtual environment active for the remaining installer commands.

---

## 4. Create the local environment file

Create `.env` from the public example file.

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### macOS or Linux

```bash
cp .env.example .env
```

Open `.env`.

You will add the private Notion and Make tokens during the next steps.

Do not share or publish `.env`.

The installer reads these values locally to authenticate API requests. It does not write the secret values to public reports.

---

## 5. Set up Notion

### 5.1 Duplicate the template

Open the [Weft Notion template](https://weft-template.notion.site/Weft-3ae38e363cc580f8b137e96d8e6633fa).

1. Click **Duplicate**.
2. Log in to Notion when prompted.
3. Select the workspace where you want to install Weft.
4. Wait until the complete page has been copied.

The duplicated template must contain:

* Archive
* Projects
* Daily Log
* Error Logs

You do not need to compare every property manually. The installer checks whether the required Notion resources are available.

If a duplicated database has a disconnected or incorrect relation, use the targeted recovery steps in [`setup/notion/database-schema.md`](./setup/notion/database-schema.md) before troubleshooting the installer.

For a technical property overview, see:

```text
setup/notion/database-schema.md
```

### 5.2 Create the Notion integration

1. Open the duplicated Weft page.
2. Click the three dots in the top-right corner.
3. Open **Connections**.
4. Click **Developer portal**.
5. Click **New integration**.
6. Select **Access token**.
7. Enter a recognizable name, for example:

```text
Weft
```

8. Copy the token immediately and store it safely. The full token is not shown again later.
9. Add it to `.env`:

```dotenv
NOTION_INSPECT_TOKEN="<notion-token>"
```

10. Enable at least:

    * read content;
    * update content;
    * insert content;
    * read user information, including email addresses.
11. Open **Content access**.
12. Add the duplicated Weft page.
13. Confirm that the four databases are included.

Notion normally adds the databases below the page automatically. They may appear light grey with **Already added**. Add a missing database manually when necessary.

14. Return to the Weft page or one of the databases.
15. Confirm that the integration is visible under **Connections**.

The Notion token belongs in `NOTION_INSPECT_TOKEN`, not in `MAKE_API_TOKEN`.

---

## 6. Prepare Make

### 6.1 Select the target team

Log in to Make and select the organization and team where Weft must be installed.

For a clean installation, use an empty team or a team without another Weft installation.

You do not need to copy the organization or team IDs. The installer discovers them later.

### 6.2 Add the Make zone to `.env`

Look at the beginning of the Make URL in your browser.

```text
https://eu1.make.com/  →  eu1
https://eu2.make.com/  →  eu2
https://us1.make.com/  →  us1
```

Add your zone to `.env`:

```dotenv
MAKE_ZONE="eu1"
```

### 6.3 Create one Make API token

1. Click your profile name or avatar.
2. Click **Profile**.
3. Open **API Access**.
4. Click **Add token**.
5. Enter a recognizable name:

```text
Weft installer
```

6. Select these permissions in the order shown in Make:

   * Connections: View
   * Organizations: View
   * Scenarios: View
   * Scenarios: Modify
   * Teams: View
   * User Defined Types: View
   * User Defined Types: Modify

The corresponding scopes are:

```text
connections:read
organizations:read
scenarios:read
scenarios:write
teams:read
udts:read
udts:write
```

7. Save the token.
8. Copy it immediately and store it safely.
9. Add it to `.env`:

```dotenv
MAKE_API_TOKEN="<make-token>"
```

Hooks and MCP scopes are not required by the installer.

### 6.4 Create the Make Notion connection

The installer binds the imported scenarios to an existing Make connection. Create the connection before running preflight.

1. Open **Scenarios**.
2. Click **Create a new scenario**.
3. Add the Notion module **Create a Data Source Item**.
4. Click **Create a connection**.
5. Select **Notion Internal**.
6. Enter:

```text
weft-make-notion-connection
```

7. Paste the Notion token stored in `NOTION_INSPECT_TOKEN`.
8. Use **ID finder** and search for **Archive**.
9. Select the Archive database.
10. Enter a temporary title:

```text
Notion connection
```

11. Save the module.
12. Choose **Save anyway** when Make reports that the temporary module is incomplete.

Keep this temporary scenario open for the next step.

### 6.5 Create the Make AI connection

Continue in the same temporary scenario.

1. Add the **Make AI Toolkit** module.
2. Select **Simple Text Prompt**.
3. Click **Add** to create a connection.
4. Enter this connection name:

```text
weft-ai-connection
```

5. Save the connection.
6. Select **Small** as the model.
7. Enter this temporary text:

```text
Weft AI provider connection
```

8. Save the module.
9. Save the scenario and choose **Save anyway**.

You may ignore these warnings in the temporary scenario:

```text
Data source ID: Value must not be empty
Input method: Value must not be empty
```

Confirm that both connections are visible under:

```text
Credentials → Connections
```

The temporary scenario is not part of Weft and may be deleted after both connections exist.

---

## 7. Configure the Make target

At this point, `.env` must contain:

```dotenv
MAKE_ZONE="your-zone"
MAKE_API_TOKEN="<make-token>"
NOTION_INSPECT_TOKEN="<notion-token>"
```

Run:

### Windows

```powershell
python -m installer configure
```

### macOS or Linux

```bash
python3 -m installer configure
```

The installer:

1. derives the Make API base URL from `MAKE_ZONE`;
2. discovers accessible organizations;
3. discovers teams;
4. selects automatically when there is one valid option;
5. asks you to choose by name when several options exist;
6. writes only these non-secret values to `.env`:

```dotenv
MAKE_API_BASE_URL="https://your-zone.make.com/api/v2"
MAKE_ORGANIZATION_ID="discovered-id"
MAKE_TEAM_ID="discovered-id"
```

A successful result contains:

```json
{
  "environment_file": "C:\\path\\to\\Weft\\.env",
  "make_zone": "eu1",
  "organization": "<selected organization>",
  "secrets_written": false,
  "status": "CONFIGURED",
  "team": "<selected team>",
  "written_keys": [
    "MAKE_API_BASE_URL",
    "MAKE_ORGANIZATION_ID",
    "MAKE_TEAM_ID"
  ]
}
```

Confirm:

* `status` is `CONFIGURED`;
* `secrets_written` is `false`;
* the organization and team are correct.

---

## 8. Run preflight

Preflight is read-only.

### Windows

```powershell
python -m installer preflight
```

### macOS or Linux

```bash
python3 -m installer preflight
```

The default terminal output is a compact summary. The complete technical report is stored privately at:

```text
.weft-installer/preflight-report.sanitized.json
```

A successful result must show:

* `status`: `PREFLIGHT_PASSED`;
* the intended organization and team;
* four Notion databases found;
* four Data Structures planned;
* five scenarios planned;
* zero Make mutations;
* zero Notion mutations.

Do not run `install` when preflight reports a block.

Resolve only the reported issue and rerun preflight.

---

## 9. Install Weft

This command creates the target-specific Make resources.

### Windows

```powershell
python -m installer install
```

### macOS or Linux

```bash
python3 -m installer install
```

The installer:

1. creates or safely reuses four Make Data Structures;
2. creates five Make scenarios;
3. captures their new scenario IDs;
4. binds dependent scenarios to the new IDs;
5. replaces Notion, connection, and Data Structure bindings;
6. reads the resources back;
7. verifies scenario structures and dependencies;
8. configures the required schedules as On demand;
9. leaves all five scenarios inactive;
10. stores private recovery state under `.weft-installer/`.

The scenarios are:

* `archive_conversation`
* `notion_text_formatter`
* `search_archive`
* `get_context`
* `create_daily_log`

When installation fails, do not immediately delete resources or restart.

Read the reported error and use `.weft-installer/` only for troubleshooting and safe recovery.

---

## 10. Verify the installed resources in Make

Open the selected Make team and confirm:

* three Weft Data Structures exist;
* five Weft scenarios exist;
* all five scenarios are inactive;
* the scenarios are in the intended team.

---

## 11. Add the scenario descriptions

Open each scenario in Make, add the matching description, and save the scenario.

Do not change inputs, outputs, mappings, modules, or scheduling.

### `archive_conversation`

```text
Archives a conversation to Notion. Use only on explicit archive request. Store input exactly as given. Do not generate or convert timestamps. Required: conversation_id, title, project, extraction_type, messages, start_time.
```

### `search_archive`

```text
Searches the Weft Notion archive for stored conversations using a title, keyword, project, date, category, or other available search criteria. Returns matching archive records and their identifying metadata.
```

### `get_context`

```text
Retrieves the complete stored content and context of a specific archived conversation from Weft. Use this tool after identifying the correct archive record through search or when the archive title is already known.
```

### `notion_text_formatter`

```text
Internal helper scenario that converts Notion archive content into a normalized text format for context retrieval. This scenario is called by get_context and is not intended for direct use by MCP clients.
```

### `create_daily_log` — optional

```text
Creates or updates the Daily Log in Notion by combining the current day’s work-session summaries, generating a concise AI summary, extracting follow-up actions, and storing the structured result.
```

---

## 12. Activate the scenarios for the current test round

The installer intentionally leaves all scenarios inactive.

### Round 1

Activate:

* `archive_conversation`
* `search_archive`

Keep inactive:

* `get_context`
* `notion_text_formatter`
* `create_daily_log`

### Round 2

After completing Round 1:

1. deactivate `archive_conversation`;
2. deactivate `search_archive`;
3. activate `get_context`;
4. activate `notion_text_formatter`.

Refresh the MCP client connection after changing the active scenarios.

---

## 13. Connect ChatGPT to Make MCP

The interface below was live-tested on 6 August 2026.

1. Click your profile.
2. Open **Settings**.
3. Open **Plugins**.
4. Open **Developer mode**.
5. Enable developer mode. Without it, you cannot add the custom MCP connection.
6. Return to **Plugins**.
7. Click **View plugins**.
8. Click the **+** button.
9. Enter:

```text
Name: Weft
Description: Weft environment for archiving conversations, searching archives, and retrieving stored context through Make and Notion.
Connection: https://mcp.make.com
Authentication: OAuth
```

10. Confirm that you understand and want to continue.
11. Click **Sign in with Weft**, or the name you assigned to the connection.
12. Select the correct Make organization.
13. Under **Run your scenarios**, select:

```text
Execute any active and on-demand scenarios using MCP
```

14. Click **Allow**.
15. Return to ChatGPT and refresh the Weft plugin.

After changing active Make scenarios, refresh ChatGPT before testing the new tools.

---

## 14. Connect Claude to Make MCP

1. Click your profile.
2. Open **Settings**.
3. Open **Connectors**.
4. Click **Add**.
5. Click **Add custom connector**.
6. Enter a recognizable name:

```text
Weft
```

7. Enter the remote MCP server URL:

```text
https://mcp.make.com
```

8. Leave advanced settings empty unless you intentionally need them. OAuth may be added for additional authorization.
9. Click **Connect**.
10. Select the correct Make organization.
11. Under **Run your scenarios**, select:

```text
Execute any active and on-demand scenarios using MCP
```

12. Click **Allow**.

A remote MCP server URL that already exists cannot be added a second time. Reuse or remove the existing connector when necessary.

After changing active Make scenarios, refresh the Claude connector before testing the new tools.

---

## 15. Run the acceptance test

Use one unique conversation ID consistently throughout the acceptance test.

Replace the timestamp fragment before running the test.

Example convention:

```text
weft-install-test-YYYYMMDD-HHMM
```

Also provide the actual start time when invoking `archive_conversation`.

### 15.1 Archive with ChatGPT — Round 1

Open a new ChatGPT conversation, add the Weft connector with the **+** button, and paste:

```text
Archive the following test conversation using the archive_conversation tool.

conversation_id: weft-install-test-YYYYMMDD-HHMM
title: Weft clean-install acceptance test
project: Weft
extraction_type: conversation
start_time: HH:MM
messages:
This is a sanitized end-to-end acceptance test for the Weft clean installation.
The exact stored content must remain retrievable without shortening or summarization.
```

Confirm that exactly one Archive record was created in the duplicated Notion workspace for this conversation ID.

### 15.2 Search with ChatGPT — Round 1

Continue in the same conversation or open a new one with the Weft connector and paste:

```text
Search the Weft archive for conversation_id weft-install-test-YYYYMMDD-HHMM using the search_archive tool. Return the matching record and identifying metadata.
```

Confirm that the returned conversation ID matches the archived record.

### 15.3 Switch to Round 2

On a Make Free plan:

1. deactivate `archive_conversation`;
2. deactivate `search_archive`;
3. activate `get_context`;
4. activate `notion_text_formatter`;
5. refresh the ChatGPT or Claude connection.

### 15.4 Retrieve the full context with Claude — Round 2

Paste:

```text
Retrieve the complete stored content of conversation_id weft-install-test-YYYYMMDD-HHMM using the get_context tool. Do not shorten or summarize the stored content.
```

Expected:

* the correct record is found;
* `notion_text_formatter` runs as the internal dependency;
* the complete stored content is returned;
* the content is not shortened or summarized.

You may repeat the same retrieval test in ChatGPT after refreshing its connector.

---

## 16. Verify the final result in Notion

Confirm:

* the test conversation exists exactly once in Archive;
* the conversation ID is correct;
* the full content is stored;
* search and retrieval used the same record;
* no unexpected entry exists in Error Logs;
* a Daily Log entry exists when the configured daily-log flow has run.

You do not need to run `create_daily_log` manually as a separate acceptance test.

---

## 17. Installation complete

### Local configuration

* [ ] The repository was cloned or extracted into a clean local folder.
* [ ] A new `.venv` was created.
* [ ] Dependencies were installed from `requirements.txt`.
* [ ] `python -m pip check` passes.
* [ ] `.env` was created from `.env.example`.
* [ ] `MAKE_ZONE` is correct.
* [ ] `MAKE_API_TOKEN` is present.
* [ ] `NOTION_INSPECT_TOKEN` is present.
* [ ] `configure` passes.
* [ ] The intended organization and team were selected.

### Notion

* [ ] The template is duplicated.
* [ ] Archive, Projects, Daily Log, and Error Logs exist.
* [ ] The integration has access to the Weft page and databases.
* [ ] Test records are written only to the duplicated workspace.

### Make

* [ ] The API token has all seven required scopes.
* [ ] The Notion connection exists.
* [ ] The Make AI connection exists.
* [ ] `preflight` passes with zero mutations.
* [ ] `install` passes.
* [ ] Four Data Structures exist.
* [ ] Five inactive scenarios exist.
* [ ] Required scenarios are configured as On demand.
* [ ] Scenario IDs and dependencies are rebound correctly.
* [ ] Scenario descriptions are added.

### Runtime and MCP

* [ ] `archive_conversation` creates the test record.
* [ ] `archive_conversation` Routes 1–7 pass, including whitespace validation, both no-write conflicts, and missing-Project relation repair.
* [ ] `search_archive` returns the same record.
* [ ] `get_context` returns the complete stored content.
* [ ] `notion_text_formatter` runs as the internal helper.
* [ ] ChatGPT connects to the Make MCP Server.
* [ ] Claude connects to the same Make MCP Server.
* [ ] The Make active-scenario limit is respected.
* [ ] No secret or private installer report has been published.

A local or mocked test is not a completed installation.

The installation is complete only after the clean-install flow succeeds in the target Notion, Make, and MCP client environments used for acceptance.