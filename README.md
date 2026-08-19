# Weft

[![Validate](https://github.com/nadira-busse/weft/actions/workflows/validate.yml/badge.svg)](https://github.com/nadira-busse/weft/actions/workflows/validate.yml)

Weft started with a recurring problem in my own AI work: important project context was spread across conversations, and continuing work elsewhere often meant rebuilding part of that context first. I began storing selected conversations, decisions and workflow output as structured records that I could search and retrieve later.

The AI landscape has changed since then. Project memory, past-chat retrieval and persistent context are now much more capable in mainstream AI products. Weft remains valuable because it makes the context layer explicit: conversations, decisions and workflow output are stored in a system that can be inspected, queried, tested and reproduced independently of any single AI client.

As a portfolio project, Weft shows how I design AI workflow infrastructure with clear orchestration, structured storage, retrieval, explicit contracts and traceable behavior.

Technically, Weft is an archive-first reference implementation built with Make, Notion and MCP-enabled AI clients. Make handles orchestration, Notion is the human-readable source of record, and three public workflows provide archive, search and context-retrieval operations.

The repository includes the canonical Make blueprints, public contracts and schemas, sanitized fixtures, regression evidence, and a Python installer for repeatable provisioning.

## Public workflows

| Scenario | Responsibility | Status |
|---|---|---|
| `archive_conversation` | Validate and create or update a durable archive record | Core MCP contract |
| `search_archive` | Return bounded archive candidates through five established routes | Core MCP contract |
| `get_context` | Return full persisted content through four established routes | Core MCP contract |

Two additional workflows support the implementation:

- `weft_notion_text_formatter` is an internal deterministic child workflow used by `get_context`.
- `weft_create_daily_log` is an optional scheduled summary workflow and is not part of the public MCP contract.

## Inspect the workflows in Make

The Weft scenarios are also available as public Make scenario pages. These pages let you inspect the actual workflows in Make and use Make's native **Use this scenario** flow when you want to reuse an individual scenario.

- [`archive_conversation`](https://eu1.make.com/public/shared-scenario/UrKrdWWmdo8/weft-archive-conversation)
- [`search_archive`](https://eu1.make.com/public/shared-scenario/kMLUtxQJb2L/weft-search-archive)
- [`get_context`](https://eu1.make.com/public/shared-scenario/vH1RABSc2t1/weft-get-context)
- [`notion_text_formatter`](https://eu1.make.com/public/shared-scenario/CxwoCdhvFcx/weft-notion-text-formatter)
- [`create_daily_log`](https://eu1.make.com/public/shared-scenario/HXO6dZj0Leo/weft-create-daily-log)

The public scenario pages are useful for direct inspection and selective reuse. A copied scenario still requires environment-specific connections, Notion resources, Data Structures and, where applicable, scenario dependencies to be configured in the target Make environment.

For a complete Weft installation, use the reproducible installer path documented in [`SETUP.md`](./SETUP.md).

## What is reproducible

Weft is published as a reference implementation rather than a zero-touch deployment package.

The public installer automates the repeatable Make provisioning work, including target discovery, dependency rebinding, candidate validation, scenario creation and read-back verification. A small manual boundary remains for external platform actions such as Notion template duplication, connection authorization, MCP exposure and final live acceptance.

The recorded evidence for the current public implementation includes:

- A full clean installation and acceptance using new Notion, Make, ChatGPT and Claude accounts passed on 6 August 2026.
- All three public MCP workflows passed manual acceptance in both ChatGPT and Claude.
- The `archive_conversation` V4 Route 1–7 regression run passed on 6 August 2026. The expected MCP/Make response was produced for every route class, and all manual assertions defined by the test procedure were verified and confirmed.
- The repository validation suite includes installer unit tests, schema and fixture validation, internal-link validation and a publication audit. The same validation sequence runs in GitHub Actions on push and pull request.

The [V4 regression report](./regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md) records the exact persistence, relation, normalization, precondition and no-change assertions covered by that test run.

The detailed verification boundaries and acceptance evidence are documented in [`setup/verification.md`](./setup/verification.md).

Runtime acceptance belongs to the revision that was actually tested. Local validators and mocked installer tests do not themselves rerun Make, Notion, ChatGPT or Claude, so a later canonical blueprint revision still requires fresh live acceptance before the same runtime claim can be made for that revision.

## Established retrieval behavior

The accepted `get_context` routes are:

- query;
- conversation ID;
- exact date;
- project.

Exact-date retrieval requires equal `date_from` and `date_to` values.

The accepted `search_archive` routes are:

- conversation ID;
- exact date;
- date range;
- project;
- query.

These routes are part of the current public behavior and should not be redesigned as part of installation or rebinding.

## Source of truth

Canonical Make exports live in [`setup/Make/blueprints/`](./setup/Make/blueprints/).

Their modules, routes, filters and mappings are the implementation source of truth. Source-environment connection, scenario, Data Structure and Notion resource IDs remain in the exports to preserve the canonical scenario structure. The installer resolves the target environment and replaces those bindings in generated candidates without modifying the canonical exports.

The public client contract is defined through:

- [`contracts/payload-contract.md`](./contracts/payload-contract.md)
- [`schemas/`](./schemas/)
- [`examples/public-contracts/`](./examples/public-contracts/)

## Reproduce Weft

For a first-time installation, clone or download a clean copy of this repository and follow [`SETUP.md`](./SETUP.md).

That document is the canonical end-to-end installation guide. The files under [`setup/`](./setup/) provide supporting technical reference material rather than a second installation procedure.

The primary Make provisioning path is the public installer documented in [`installer/README.md`](./installer/README.md). Manual blueprint import followed by per-module rebinding is not the supported end-user installation path.

The tested local Python runtime is Python 3.13.3. Broader Python-version compatibility has not been established.

Run the repository checks from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s installer/tests -p "test_*.py" -v
python scripts/validate_examples.py
python scripts/check_internal_links.py
python scripts/audit_publication.py
```

Current platform, installer and export boundaries are documented in [`setup/known-limitations.md`](./setup/known-limitations.md).

## Repository map

| Directory                                  | Responsibility                                                                              |
| ------------------------------------------ | ------------------------------------------------------------------------------------------- |
| [`architecture/`](./architecture/)         | System boundaries, layer model and engineering principles                                   |
| [`systems/`](./systems/)                   | Write- and read-side implementation documentation and system-local evidence                 |
| [`contracts/`](./contracts/)               | Public payload behavior                                                                     |
| [`schemas/`](./schemas/)                   | Request and response JSON Schemas                                                           |
| [`examples/`](./examples/)                 | Sanitized valid and invalid public-contract fixtures                                        |
| [`regression-tests/`](./regression-tests/) | Sanitized V4 route fixtures and the canonical `archive_conversation` regression report      |
| [`installer/`](./installer/)               | Public Make configuration, preflight, provisioning, recovery and read-back verification CLI |
| [`setup/`](./setup/)                       | Supporting Notion, Make, connection, Data Structure and verification references             |
| [`scripts/`](./scripts/)                   | Deterministic repository validation and publication checks                                  |

Representative runtime-history screenshots are stored with the systems they document:

* [`systems/archive-conversation/`](./systems/archive-conversation/)
* [`systems/context-retrieval/`](./systems/context-retrieval/)

They are historical runtime evidence, not proof of a later clean-account installation.

## License

Weft is licensed under the [Apache License 2.0](./LICENSE).
