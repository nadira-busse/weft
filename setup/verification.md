# Verification Evidence Reference

The canonical first-time verification sequence is part of [`../SETUP.md`](../SETUP.md). This reference defines evidence categories and detailed acceptance checks; it is not a second installation procedure.

Use `configured`, `statically inspected`, `API-verified`, `runtime-tested`, `manually verified`, or `pending`. Record a date, environment label, and sanitized evidence reference for completed clean-install stages.

The owner’s existing ChatGPT and Claude environments passed manual runtime acceptance for all public MCP scenarios. A full clean installation with new Notion, Make, ChatGPT, and Claude accounts passed on 6 August 2026. The [`archive_conversation` V4 report](../regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md) records the expected MCP/Make response and confirms every manual assertion defined by the test procedure for all seven route classes on 6 August 2026. This confirmation covers the listed persistence, relation, normalization, precondition, and no-change assertions, not every theoretically possible side effect. These are acceptance records for the versions and evidence layers tested, not proof of a later canonical blueprint revision.

## Repository and mocked-installer validation

| Check | Command | Status in each clone |
|---|---|---|
| Parse JSON, validate schemas/public fixtures and all seven V4 regression suites, and guard blueprint output specs | `python scripts/validate_examples.py` | pending until run |
| Check Markdown links | `python scripts/check_internal_links.py` | pending until run |
| Scan public files, `.env.example`, placeholders, paths, and secret-like material | `python scripts/audit_publication.py` | pending until run |
| Exercise installer preflight, creation, ID propagation, resume, ambiguity, and reporting with doubles | `python -m unittest discover -s installer/tests -p "test_*.py" -v` | pending until run |

Mocked tests prove deterministic local behavior only; they make no live Make or Notion request.

## Notion resources

- [ ] `manually verified` — `Archive`, `Projects`, `Daily Log`, and `Error Logs` exist in the duplicated workspace.
- [ ] `configured` — The Notion integration used by the installer and the selected Make Notion connection can access all four resources.
- [ ] `API-verified` — Public installer preflight resolves every data source and property mapping uniquely.

## Installer preflight

Run `python -m installer preflight` and verify:

- [ ] `configured` — The Make API token has all required scopes.
- [ ] `API-verified` — Team/organization IDs match the intended target.
- [ ] `API-verified` — Exactly one valid Notion connection is selected or explicitly configured.
- [ ] `API-verified` — Exactly one UI-visible/scoped `ai-provider` connection is selected or explicitly configured.
- [ ] `statically inspected` — Five canonical blueprints and four Data Structure contracts validate.
- [ ] `statically inspected` — All structural replacement targets and the dependency graph resolve.
- [ ] `API-verified` — Reported Make and Notion mutation counts are zero.

If `MANUAL_UI_CONNECTION_REQUIRED` is returned, complete the AI-provider connection step in [`../SETUP.md`](../SETUP.md), then rerun preflight.

## Provisioning and static read-back

Run `python -m installer install` and review `.weft-installer/installation-report.json` locally:

- [ ] `configured` — Four required Data Structures are created or uniquely reused.
- [ ] `configured` — All five scenarios have newly created or state-reconciled target IDs.
- [ ] `statically inspected` — `get_context` references the newly installed formatter ID.
- [ ] `statically inspected` — Connections, Notion resources/properties, Data Structures, and scenario references have no unresolved source binding at executable paths.
- [ ] `statically inspected` — Scenario topology, routes, filters, mappings, and public interfaces compare exactly after read-back, except deterministic target bindings.
- [ ] `statically inspected` — `create_daily_log` resolves the Daily Log by exact `Date` and uses the installer-managed `Weft - Daily Log Content` parser structure.
- [ ] `statically inspected` — `create_daily_log` module 43 retains provider family `ai-provider` and model `small`.
- [ ] `API-verified` — Every scenario reads back in the configured team and inactive.
- [ ] `configured` — Installer status is `LOCALLY_VERIFIED_CLEAN_INSTALL_PENDING`.

## Scenario runtime tests

Use sanitized data. Activate only the minimum scenario set needed for each test and return all installer-created scenarios to the intended inactive state afterward.

- [ ] `runtime-tested` — `archive_conversation` creates one record for a new stable ID and updates rather than duplicates on repetition.
- [ ] `runtime-tested` — `archive_conversation` Routes 1–7 pass, including whitespace rejection, both strict no-write conflicts, and missing-Project relation repair.
- [ ] `runtime-tested` — `search_archive` passes conversation-ID, exact-date, date-range, project, and query routes.
- [ ] `runtime-tested` — `search_archive` returns `key_insights`, `model_origin`, dynamic limits, structured empty results, and validation envelopes.
- [ ] `runtime-tested` — `get_context` passes conversation-ID, query, exact-date, and project routes.
- [ ] `runtime-tested` — `get_context` returns full/long content, `message_count`, `content_length`, route-specific `retrieval_mode`, empty results, and validation envelopes.
- [ ] `runtime-tested` — Exact-date `get_context` uses equal dates and preserves the established formatter input selection and full-content assembly behavior.
- [ ] `runtime-tested` — Optional `create_daily_log` updates a sanitized record, if in scope, using the installed `Weft - Daily Log Content` parser structure.
- [ ] `API-verified` — All installer-created scenarios are inactive at the end unless activation was explicitly accepted.

## MCP client acceptance

Prior established results:

- ChatGPT MCP client: `runtime-tested` and passed in the owner’s existing environment.
- Claude MCP client: `runtime-tested` and passed in the owner’s existing environment.
- All three public scenarios: `runtime-tested` and passed in both existing client environments.

For each newly provisioned or changed installation:

- [ ] `pending` — Expose only `archive_conversation`, `search_archive`, and `get_context`.
- [ ] `runtime-tested` — ChatGPT repeats the public regression set against the newly installed scenarios.
- [ ] `runtime-tested` — Claude repeats the same set against the newly installed scenarios.
- [ ] `manually verified` — Client-visible names and descriptions match the public contracts.

## Clean-environment and revision acceptance

- [x] `runtime-tested` — The complete public entrypoint ran in new Notion, Make, ChatGPT, and Claude accounts on 6 August 2026.
- [x] `manually verified` — The public instructions were followed without relying on committed private installer state.
- [ ] `pending` — After the synchronized canonical revision is published, repeat fresh installer provisioning and Make import/provisioning of the modified Archive blueprint.
- [ ] `pending` — Repeat MCP regression Routes 1–7 and verify Notion state, record identity, relation repair, and conflict non-mutation.
- [ ] `pending` — Repeat ChatGPT and Claude MCP verification against the published revision's scenarios.
- [ ] `pending` — Compare Data Structures, interfaces, topology, mappings, dependencies, and behavior semantically; ignore environment-specific IDs.
- [ ] `pending` — Preserve a sanitized post-change report and record the exact manual connection boundary.

Until the post-change stage passes, describe this revision as statically verified with fresh post-change live acceptance pending. Do not erase or reinterpret the earlier successful clean-account record or broaden the V4 report beyond its confirmed tool-response evidence and defined manual assertions.
