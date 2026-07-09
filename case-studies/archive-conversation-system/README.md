# Case Study — Archive Conversation System

## Overview

The Archive Conversation System implements the write-side of Weft.

It turns selected AI interactions, workflow outputs and project decisions into structured archive records that can be stored, linked and retrieved later.

This part of the system focuses on reliable capture and persistence.

---

## Problem

AI-assisted work often starts as temporary interaction: a chat message, generated output, workflow result or decision made during a session.

Without a reliable archive layer, that work remains fragile:

* useful context disappears inside conversations
* decisions are hard to find later
* retries can create duplicate records
* project state becomes scattered
* future AI sessions cannot reliably continue from earlier work

The archive system solves this by creating a stable system of record for meaningful AI-assisted work.

---

## Objective

The objective is to persist each logical interaction as a structured archive record with predictable write behavior.

The system must support:

* stable identifiers
* one clear archive write path
* explicit create/update behavior
* relationship resolution before writing
* retry-safe execution
* clear write confirmation after storage

A retry should not create a second record for the same logical interaction. It should converge on the same persisted archive state.

---

## Scope

This case study covers the archive write path only: receiving a structured archive request, normalizing the payload, resolving identifiers and relations, checking whether the archive record already exists, and writing the result to the archive system of record.

It does not cover what happens after storage, such as searching the archive, selecting relevant records for a future session, or using archived records to update project documentation.

This keeps the case study focused on reliable capture and persistence.

---

## Architecture Boundary

```text
AI Client / Workflow Client
↓
Invocation Interface
↓
Orchestration Layer
↓
Context & Logic Layer
↓
Data Layer
```

Each layer has a distinct responsibility.

The AI client can request archiving, but it does not own persistence.

The invocation interface is the controlled entry point into the archive workflow.

The orchestration layer controls workflow behavior.

The data layer stores records and relations, but it does not decide workflow logic.

---

## Archive Write Flow

```text
interaction or workflow output
↓
archive request
↓
payload normalization
↓
identifier resolution
↓
relationship resolution
↓
existence check
↓
create or update
↓
write confirmation
```

The write order is explicit so the workflow does not create or update records before the payload, identifiers, relations and existence state are known.

---

## Deterministic Write Strategy

The system uses an existence-first write model.

Before writing, the workflow checks whether a matching archive record already exists.

Routing is based on lookup cardinality:

| Lookup result | Behavior |
| --- | --- |
| 0 records | Create a new archive record |
| 1 record | Update the existing archive record |
| Multiple records | Treat as a data integrity error and stop the write path |

When lookup is based on the stable archive identifier, multiple matches should not occur. If they do, the workflow treats this as a data integrity issue instead of choosing one record silently.

A repeated archive request with the same stable identifier should target the same logical archive record instead of creating duplicates.

---

## Public Data Model

The public architecture exposes only the conceptual model.

The system works with three core record types:

* archive record
* project record
* daily log record

An archive record can be related to:

* a project
* a daily log
* source metadata

Internal database structures, exact Notion properties, private identifiers and full record payloads are intentionally not published.

Public payload examples are documented in [`examples/public-contracts/`](../../examples/public-contracts/).

---

## Failure Modes Addressed

The archive write path was designed around real workflow failure conditions.

| Failure mode | Risk | Mitigation |
| --- | --- | --- |
| Retry-induced duplicate writes | A retry creates a second record for the same logical interaction | Resolve identifiers before writing and check existence before create |
| Lookup misinterpretation | A valid “not found” state is treated as an error | Separate validation from lookup and route zero results explicitly |
| Relation mapping errors | Records are created without required or correct relations | Resolve and validate relationship identifiers before writing |
| Partial execution | A workflow stops before the archive operation is complete | Reuse stable identifiers so retries target the same archive record |

---

## Patterns Applied

The archive write path applies reusable workflow architecture patterns documented in [`patterns/`](../../patterns/), especially idempotent archive writes, explicit existence checks and relation identifier mapping.

---

## Trade-offs

| Decision | Benefit | Cost |
| --- | --- | --- |
| Archive-first persistence | Stronger continuity and traceability | More write operations and relation handling |
| Deterministic write path | More predictable workflow behavior | More explicit routing logic |
| Idempotent writes | Safer retries and duplicate prevention | Requires stable identifier discipline |
| Existence-first routing | Clear create/update behavior | Additional lookup step before writing |
| Human-readable system of record | Easier inspection and debugging | Not optimized for high-scale storage |
| Visual orchestration | Fast iteration and visible debugging | Less flexible than custom code |

---

## Outcome

The archive write path gives Weft a reliable write-side foundation.

Selected AI-assisted work is no longer left only in temporary chats. It becomes a structured archive record with a stable identifier, explicit relations and predictable create/update behavior.

---

## Related

* [`Context Continuity System`](../context-continuity-system/)
* [`Payload Contracts`](../../contracts/payload-contract.md)
* [`Public Contract Examples`](../../examples/public-contracts/)
* [`Patterns`](../../patterns/)
