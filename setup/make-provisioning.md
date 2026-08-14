# Make Provisioning Reference

The canonical first-time installation sequence is [`../SETUP.md`](../SETUP.md). This reference describes how the public installer provisions and verifies the five Make scenarios; it is not an alternative installation procedure.

The installer uses the canonical exports in [`Make/blueprints/`](./Make/blueprints/) and never writes target IDs back into them. Manual per-module rebinding is not a supported end-user workflow.

## Provisioning entrypoints

The public commands are:

```powershell
python -m installer configure
python -m installer preflight
python -m installer install
```

`configure` derives the Make API base URL from `MAKE_ZONE`, discovers accessible organizations and teams, lets the user select the target when necessary, and writes only the selected non-secret target values to `.env`.

`preflight` is read-only. It validates configuration and scopes, the target boundary, five blueprint files, four Data Structure contracts, the dependency graph, Notion resources, connection uniqueness, and every structural replacement target. It builds in-memory candidates using synthetic future IDs and reports zero Make and Notion mutations.

`install` repeats preflight before provisioning. The required environment preparation, connection authorization, and command order are documented only in [`../SETUP.md`](../SETUP.md).

## Provisioning behavior

The installer:

1. creates or deterministically reuses the four structures described in [`data-structure.md`](./data-structure.md);
2. creates `notion_text_formatter`, `archive_conversation`, `search_archive`, optional supporting `create_daily_log`, and `get_context`;
3. captures every new Make scenario ID;
4. injects the new formatter ID into all `get_context` child calls;
5. replaces source connection, Data Structure, Notion data-source, property, relation-metadata, and scenario-reference bindings at typed paths;
6. reads scenarios, blueprints, and public interfaces back from Make;
7. verifies names, team, topology, complete stored definitions, interfaces, dependencies, and inactive state;
8. writes resumable state and full/sanitized reports.

All scenarios are submitted on demand and left inactive. The installer does not run scenarios, activate them, or configure a schedule.

## Reports and recovery

The installer writes local state and reports under `.weft-installer/`:

- `installation-state.json` — target-bound resume state;
- `installation-report.json` — full local report with IDs;
- `installation-report.sanitized.json` — shareable report without IDs;
- `installation-error.json` — fail-closed recovery information, when applicable;
- `installation-error.sanitized.json` — shareable failure report without target IDs;
- `candidates/` — generated target blueprints and path-level binding manifests.

The full state, reports, and candidates remain local because they contain target identifiers. The installer writes each returned ID before later verification and reads recorded resources back before reuse. Mutation calls are not blindly retried. An ambiguous create is reconciled by exact installer name and full contract; non-unique results stop with `retry_safe: false`. No resource is automatically deleted.

Without recorded state, an exact scenario-name collision fails closed rather than adopting an unproven resource. Preserve the inactive resources and reports after a failure so the installer can reconcile observed state safely.

## Verification and activation boundary

The installer status `LOCALLY_VERIFIED_CLEAN_INSTALL_PENDING` proves local candidate checks and Make API read-back for that run. It does not prove scenario runtime or client acceptance.

Only after the verification flow in [`../SETUP.md`](../SETUP.md) should an installation expose or activate:

- `archive_conversation`, `search_archive`, and `get_context` as public MCP scenarios;
- `notion_text_formatter` only for internal child execution;
- `create_daily_log` only when the optional workflow is required and its runtime behavior has been verified.

Every published canonical blueprint revision requires fresh provisioning and live acceptance before it can inherit a runtime acceptance claim.

## Manual import policy

Manual blueprint import is an unsupported contributor diagnostic. With dozens of Notion modules and hundreds of exported bindings, module-by-module repair cannot provide a reproducible installation. If installer read-back fails, preserve the inactive resources and reports and diagnose the structural rule or canonical export; do not present manual rebinding as a viable user installation method.
