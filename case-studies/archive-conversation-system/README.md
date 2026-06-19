# Case Study — Archive Conversation System

## Overview

The Archive Conversation System implements the write-side of Weft.

It turns selected AI interactions, workflow outputs and project decisions into structured archive records that can be stored, linked and retrieved later.

This part of the system focuses on reliable capture and persistence.

It does not handle:

* archive search
* ranking
* context reconstruction
* knowledge promotion

Those responsibilities belong to separate retrieval and context systems.

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
* public-safe confirmation after storage

A retry should not create a second record for the same logical interaction. It should converge on the same persisted archive state.

---

## Scope

This case study covers the archive write path only.

Included:

* archive invocation
* payload normalization
* identifier resolution
* existence checks
* create/update behavior
* relation mapping
* persistence into the archive system of record

Excluded:

* archive search
* context retrieval
* ranking
* filtering
* canonical knowledge promotion

This separation keeps the write-side architecture focused and predictable.

---

## Architecture Boundary

```text id="o5qx4c"
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

The orchestration layer controls workflow behavior.

The data layer stores records and relations, but it does not decide workflow logic.

---

## Archive Write Flow

```text id="2ws2pf"
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

The workflow is intentionally explicit.

No write operation should occur before:

* the payload is normalized
* the archive identifier is resolved
* related records are checked
* the existence state is known

This prevents ambiguous writes and uncontrolled duplicate creation.

---

## Deterministic Write Strategy

The system uses an existence-first write model.

Before writing, the workflow checks whether a matching archive record already exists.

Routing is based on lookup cardinality:

|    Lookup result | Behavior                           |
| ---------------: | ---------------------------------- |
|        0 records | Create a new archive record        |
|         1 record | Update the existing archive record |
| Multiple records | Fail or route to error handling    |

This makes retries safer.

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
* workflow execution context

Internal database structures, exact Notion properties, private identifiers and full record payloads are intentionally not published.

Public payload examples are documented in [`examples/public-contracts/`](../../examples/public-contracts/).

---

## Failure Modes Addressed

The archive write path was designed around real workflow failure conditions.

| Failure mode                   | Risk                                                             | Mitigation                                                           |
| ------------------------------ | ---------------------------------------------------------------- | -------------------------------------------------------------------- |
| Retry-induced duplicate writes | A retry creates a second record for the same logical interaction | Resolve identifiers before writing and check existence before create |
| Lookup misinterpretation       | A valid “not found” state is treated as an error                 | Separate validation from lookup and route zero results explicitly    |
| Relation mapping errors        | Records are created without required or correct relations        | Resolve and validate relationship identifiers before writing         |
| Partial execution              | A workflow stops before the archive operation is complete        | Preserve stable identifiers and make retry behavior converge         |

---

## Patterns Applied

This system applies reusable workflow architecture patterns:

* Explicit Existence Check
* Get-or-Create Upsert
* Idempotent Archive Write
* Derived Record Ensure
* Relation Identifier Mapping
* Validation Before Lookup
* Immutable Field Guard

See:

See [`patterns/`](../../patterns/).

---

## Trade-offs

| Decision                        | Benefit                                | Cost                                        |
| ------------------------------- | -------------------------------------- | ------------------------------------------- |
| Archive-first persistence       | Stronger continuity and traceability   | More write operations and relation handling |
| Deterministic write path        | More predictable workflow behavior     | More explicit routing logic                 |
| Idempotent writes               | Safer retries and duplicate prevention | Requires stable identifier discipline       |
| Existence-first routing         | Clear create/update behavior           | Additional lookup step before writing       |
| Human-readable system of record | Easier inspection and debugging        | Not optimized for high-scale storage        |
| Visual orchestration            | Fast iteration and visible debugging   | Less flexible than custom code              |

---

## Outcome

The Archive Conversation System provides the write-side foundation for Weft.

It enables:

* persistent archive records
* retry-safe workflow execution
* stable project-linked context
* traceable AI-assisted work
* later retrieval and context reconstruction

The result is a system where selected AI interactions are no longer only temporary chat artifacts. They become structured records that can support continuity across sessions and tools.

---

## Related

* [`Context Continuity System`](../context-continuity-system/)
* [`Payload Contracts`](../../contracts/payload-contract.md)
* [`Public Contract Examples`](../../examples/public-contracts/)
* [`Patterns`](../../patterns/)
