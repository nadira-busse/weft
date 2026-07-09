# Pattern: Idempotent Archive Upsert

## Problem

The same logical event may be stored multiple times when workflows are retried or executed repeatedly.

For each stable event identifier, the archive should resolve to one logical record.

Repeated executions must converge on that record instead of creating duplicates.

Without this behavior, the archive can develop inconsistent state.

This can lead to:

* duplicate records
* broken relationships
* unreliable retrieval
* unreliable downstream analysis
* unclear archive state after retries

---

## Context

This pattern applies to systems that must preserve one archive record per stable logical event.

Typical examples include:

* conversation archives
* workflow output archives
* message storage systems
* event logs
* transaction records

---

## Cause

Idempotency is often assumed but not enforced.

Common causes include:

* always executing create operations
* missing existence checks
* misinterpreting lookup results
* validating input values instead of record existence
* missing or unstable identifiers
* treating retries as new events instead of reprocessing the same event

Without an explicit existence check and stable identifier, repeated executions can create multiple records for the same logical event.

---

## Solution

Use an idempotent, existence-first write strategy based on a stable event identifier.

The system must:

* derive or receive the event identifier before writing
* keep the identifier stable across retries
* avoid deriving identity from mutable content
* look up the archive record by that identifier
* branch explicitly on lookup cardinality
* create only when no matching record exists
* update only when exactly one matching record exists
* fail or resolve ambiguity when multiple records match

Routing:

| Lookup outcome     | Required behavior                    |
| ------------------ | ------------------------------------ |
| Error              | Stop or route to error handling      |
| Zero results       | Create archive record                |
| Exactly one result | Update explicitly allowed fields     |
| Multiple results   | Fail or resolve ambiguity explicitly |

This makes repeated executions converge on one archive record.

---

## Implementation

A typical implementation follows this flow:

```text
resolve stable event identifier
↓
lookup archive record by identifier
↓
route by cardinality
↓
create or update through explicit branch
↓
resolve one archive record ID
↓
continue downstream
```

All write operations must be conditioned on the lookup result.

All downstream logic must use the resolved archive record ID.

No implicit execution path should exist after lookup.

---

## Guarantees

When correctly implemented, this pattern helps ensure:

* one archive record per stable event identifier
* no duplicate archive entries under normal retry conditions
* stable archive identity across repeated executions
* deterministic create vs update behavior
* explicit handling of ambiguous matches
* safer downstream relations and retrieval

---

## When to Apply

Use this pattern when:

* each logical event should map to one archive record
* workflows may be retried or re-executed
* duplicate records would break archive integrity
* downstream retrieval depends on stable record identity
* the platform does not provide safe native upsert behavior

---

## Failure Modes

Without this pattern, systems commonly produce:

* duplicate records for the same identifier
* broken relations between records
* unreliable retrieval and reporting
* multiple records created under retry conditions
* divergence between repeated executions
* event identifiers derived from mutable fields
* repeated executions creating divergent state instead of converging

---

## Platform Notes

In systems such as Make + Notion:

* lookup operations may return empty results without errors
* existence must be evaluated explicitly
* execution may retry or partially fail
* write operations are not atomic
* stable identifiers are needed to keep repeated executions convergent

These constraints make idempotent write strategies important for archive workflows.

---

## Related Patterns

This pattern is commonly used with:

* [Explicit Existence Check](explicit-existence-check.md)
* [Get-or-Create Upsert](get-or-create-upsert.md)
* [Immutable Field Guard](immutable-field-guard.md)
* [Input Validation vs Lookup](input-validation-vs-lookup.md)
