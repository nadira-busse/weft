# Pattern: Immutable Field Guard

## Problem

A workflow updates an existing record that was found through a unique key.

Some fields represent identity, ownership or routing. They define what the record is and where it belongs.

Those fields must not change after creation.

If updates are applied without checking these fields, the workflow may overwrite record identity.

This can lead to:

* incorrect relationships between records
* cross-context data contamination
* loss of referential integrity
* records being reassigned to the wrong project, tenant or owner
* identity drift over time

---

## Context

This pattern applies to systems that:

* use idempotent update or upsert logic
* rely on stable identifiers for relationships
* enforce ownership or grouping constraints
* update existing records after lookup

Typical examples include:

* project or tenant identifiers
* conversation or event identifiers
* ownership keys
* routing keys
* source-system identifiers

---

## Cause

Update operations often assume that all fields are mutable.

Common causes include:

* applying updates without checking existing values
* relying only on lookup results without retrieving the full record
* missing validation of invariant fields before update
* treating identity fields as regular mutable data
* allowing retry logic to overwrite write-once fields

Without explicit validation, workflows may overwrite fields that define record identity or ownership.

---

## Solution

Use an immutable field validation step before any update operation.

The system must:

* retrieve the existing record when it already exists
* define which fields are immutable
* compare immutable fields against incoming values
* allow updates only when invariant fields match
* fail or route to conflict handling when a mismatch is detected
* update only explicitly allowed mutable fields

Validation must happen before any write operation is executed.

---

## Implementation

A typical implementation follows this flow:

```text id="nyafwi"
resolve target record
↓
retrieve current record state
↓
compare immutable fields
↓
if match → update allowed mutable fields
↓
if mismatch → fail or route to conflict handling
```

Immutable fields must be defined at schema or system level.

They should not be inferred during execution.

---

## Guarantees

When correctly implemented, this pattern helps ensure:

* record identity is preserved over time
* stable relationships between records
* no overwrite of immutable identifiers
* safer idempotent update behavior
* protection against cross-context data contamination
* clearer conflict handling when identity values do not match

---

## When to Apply

Use this pattern when:

* records contain write-once identifiers
* relationships depend on stable ownership or grouping
* updates occur through idempotent or retryable workflows
* data integrity must be preserved across systems
* a record may be found by one key but updated with additional incoming data

---

## Failure Modes

Without this pattern, systems commonly produce:

* overwritten identifiers
* incorrect record ownership
* broken relationships between entities
* silent data corruption
* identity drift across updates
* identity fields overwritten during retries
* records incorrectly reassigned across contexts or tenants

---

## Platform Notes

In systems such as Make + Notion:

* lookup results may not expose all fields needed for validation
* full record retrieval may be required before safe updates
* execution may retry or partially fail
* updates may overwrite fields unless explicitly controlled

These constraints make invariant validation important in update workflows.

---

## Related Patterns

This pattern is commonly used with:

* [Get-or-Create Upsert](get-or-create-upsert.md)
* [Idempotent Archive Upsert](idempotent-archive-upsert.md)
* [Relation Identifier Mapping](relation-identifier-mapping.md)
