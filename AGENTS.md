# AGENTS.md

## Purpose

Weft is a reproducible reference implementation of an archive-first AI context system using Make and Notion. These instructions guide contributors and repository agents working on public source artifacts, setup work, and acceptance testing. Weft is not presented as a one-click installer.

## Repository scope

The repository contains public canonical Make blueprints, setup instructions, contracts, schemas, verification logic, and reproducibility documentation. Environment-specific deployment state, generated candidates, credentials, and private evidence must not be committed.

## Source-of-truth files

- `setup/Make/blueprints/` contains canonical public Make source artifacts.
- `contracts/` defines public workflow behavior.
- `schemas/` contains machine-readable payload contracts.
- `SETUP.md` is the canonical end-to-end first-time installation guide.
- `setup/` contains supporting technical references and known limitations.

Canonical blueprints are source artifacts, not deployed target snapshots. Export identifiers that Make requires may be treated as rebinding inputs, but target-environment identifiers must never be promoted back into public blueprints.

## Repository layout

- `architecture/` explains system boundaries and engineering principles.
- `systems/` documents the archive and retrieval implementations.
- `contracts/`, `schemas/`, and `examples/` define public interfaces and examples.
- `SETUP.md` contains the complete installation and acceptance sequence.
- `setup/` contains Notion, Make, Data Structure, connection, and verification references.
- `scripts/` contains public repository validation tooling when present.
- `.agent-private/` may be used as an optional ignored local workspace; it is not part of the public implementation.

## Setup workflow

1. Duplicate and configure the Notion template.
2. Create the required Make connections.
3. Provision or verify the required Data Structures.
4. Generate environment-specific scenario candidates from canonical blueprints.
5. Deploy scenarios inactive.
6. Perform static read-back and fidelity verification.
7. Perform controlled runtime verification with sanitized data.
8. Leave scenarios inactive unless activation is explicitly required.

Follow `SETUP.md` for the executable installation sequence and use files under `setup/` only for supporting technical detail. Do not invent setup steps or claim automation beyond the documented and tested boundary.

## Canonical blueprint rules

Do not modify canonical blueprints casually. A functional change requires evidence of the defect, an exact path-level diff, regression tests, and runtime proof when applicable. Preserve topology, interfaces, prompts, schedules, and unrelated mappings. Never place a target environment's identifiers in public canonical files.

`create_daily_log` module 14 has this canonical filter contract:

- property: `Title (Title)`
- operator: `Text: Contains`
- value: `{{28.today}}`
- serialized selector: `Title |&*^%$#@| title`

This is a canonical contract, not a local workaround. `create_daily_log` module 43 must retain provider family `ai-provider` and model `small`; its actual connection ID is environment-specific.

## Environment-specific bindings

Discover or rebind these values for every target environment:

- Make and Notion connection IDs;
- Notion database, data-source, and property IDs;
- Make Data Structure IDs;
- subscenario IDs;
- team and organization IDs.

Generated target candidates and binding manifests belong in ignored private state. Replace identifiers only at approved semantic paths, and verify that source-environment IDs do not remain where target bindings are required.

## Testing and verification

Validate candidates locally before deployment. Verification must cover exact source-ID removal, scenario read-back, interface fidelity, static topology and mapping checks, and controlled runtime tests with sanitized inputs. Installer-created scenarios must be inactive at the end, and any maximum-active-scenario constraint must be respected.

Use only test and validation commands confirmed by the repository. Rate-limit retries must be bounded and honor server guidance. After an ambiguous create, update, or delete response, reconcile current state before deciding whether another mutation is safe; never retry blindly.

## Safety rules

- Never persist secrets or commit `.env` files.
- Never delete external resources without explicit authorization.
- Never update unrelated user resources.
- Never replay an ambiguous mutation without read-back reconciliation.
- Fail closed when the target team or organization is wrong or unproven.
- Keep public canonical files separate from private generated deployment artifacts.
- Begin external inspection read-only and require explicit authorization for external mutations.

## Documentation rules

Write repository documentation in English and make claims only from evidence. Record known limitations precisely, including manual prerequisites; do not claim full automation when a manual step is proven necessary. Do not place private IDs, private evidence, or local machine paths in public documentation. Avoid duplicating guidance across the README, setup documentation, and contracts; link to the appropriate source of truth.

## Final acceptance

Final clean-account acceptance must begin from a public clone and a fresh target environment. Verify the result semantically against the canonical Make blueprints, public contracts and schemas, public fixtures, V4 regression evidence, and the validation commands documented in `SETUP.md`. Environment-specific IDs are not acceptance criteria. Any maintainer-local checkpoint is optional context and must not be required to reproduce or accept the public implementation.

## Local private overrides

Local machine-specific and private instructions belong in `.agent-private/AGENTS.local.md`. That file is optional and is not expected in public clones. Local instructions may add stricter constraints or environment context, but must not weaken the public safety rules in this file.
