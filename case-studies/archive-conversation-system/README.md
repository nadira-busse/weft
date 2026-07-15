# Case Study — Archive Conversation System

The Archive Conversation System implements the write-side of Weft.

It turns temporary AI-assisted work into structured archive records without creating duplicates, losing required relations or leaving write behavior ambiguous.

The focus is reliable capture and persistence.

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

This routing logic follows [`patterns/explicit-existence-check.md`](../../patterns/explicit-existence-check.md) and [`patterns/idempotent-archive-upsert.md`](../../patterns/idempotent-archive-upsert.md).

---

## Record Relationships

The write path works with three core record types:

* archive record
* project record
* daily log record

An archive record can be linked to a project, a daily log and source metadata.

See [`examples/public-contracts/`](../../examples/public-contracts/) for the documented payload shapes.

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

## Trade-offs

General Weft-level trade-offs (archive-first design, Notion as system of record, Make as orchestration layer) are documented in the root [`README.md`](../../README.md) — "Trade-Offs." The trade-offs specific to the write path are:

| Decision | Benefit | Cost |
| --- | --- | --- |
| Deterministic write path | More predictable workflow behavior | More explicit routing logic |
| Idempotent writes | Safer retries and duplicate prevention | Requires stable identifier discipline |
| Existence-first routing | Clear create/update behavior | Additional lookup step before writing |

---

## Outcome

The write path produces one predictable archive record per logical interaction, with stable identity, resolved relations and explicit create/update behavior.

---

## Related

* [`Context Continuity System`](../context-continuity-system/)
* [`Archive-First Context Flow`](../../architecture/archive-conversation-flow.md)
* [`Payload Contracts`](../../contracts/payload-contract.md)
* [`Public Contract Examples`](../../examples/public-contracts/)
* [`Patterns`](../../patterns/)
