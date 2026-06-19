# Pattern: Relation Identifier Mapping

## Problem

Relations between records fail or produce inconsistent results when the wrong identifier type is used.

The system must establish relations with the correct identifier for the target entity.

Identifier correctness is not only about the value itself. It also depends on:

* identifier type
* entity scope
* source of the identifier

Typical symptoms include:

* relation fields remaining empty
* failed or rejected updates
* linked records not appearing in the interface
* relations pointing to the wrong entity type or scope

---

## Context

This pattern applies to systems where relationships between records are created through identifiers.

It is especially relevant in:

* cross-entity relationships
* multi-database or multi-table systems
* automation workflows that link records dynamically
* systems where container IDs and record IDs are different things

---

## Cause

Relation fields often require a specific identifier type.

Common causes include:

* using a container ID instead of a record ID
* mapping values from the wrong source
* manually constructing identifiers
* mixing entity identity with relation identifiers
* reusing identifiers across incompatible entity scopes

In systems such as Notion:

* relations require page-level identifiers
* database IDs or other container identifiers are not accepted as relation targets

---

## Solution

Use system-generated record identifiers returned by lookup or creation steps when mapping relations.

The system must:

* retrieve or create the target record first
* extract the correct system-generated record identifier
* confirm the identifier belongs to the expected entity type or scope
* resolve one identifier for downstream use
* pass that identifier directly into the relation mapping

Identifiers must not be inferred, transformed or manually constructed.

---

## Implementation

A typical implementation follows this flow:

```text id="t02lvi"
retrieve or create target record
↓
extract system-generated record ID
↓
resolve one downstream identifier
↓
apply identifier in relation mapping
```

When multiple execution paths exist, all branches must converge on the same identifier shape before relation assignment.

All relation operations must use the resolved system-generated identifier.

No alternative identifier source should be used unless it is explicitly validated as the correct record identifier.

---

## Guarantees

When correctly implemented, this pattern helps ensure:

* relations point to the intended record
* identifier type and scope are controlled
* empty or failed relation mappings are reduced
* cross-entity references remain consistent
* downstream workflows receive stable relationships

---

## When to Apply

Use this pattern when:

* creating or updating relationships between records
* linking entities across systems or datasets
* identifiers differ between entity types
* lookup/create results are used to build relations
* relation targets must remain stable across retries

---

## Failure Modes

Without this pattern, systems commonly produce:

* empty or broken relations
* failed updates
* inconsistent cross-entity references
* difficult-to-debug data inconsistencies
* valid-looking but non-resolvable relation assignments
* relations pointing to the wrong entity scope

---

## Platform Notes

In systems such as Make + Notion:

* relation fields require page-level identifiers
* lookup and creation operations return valid system-generated page identifiers
* incorrect mappings often come from using identifiers from the wrong entity scope or identifier type

These constraints require strict control over identifier sourcing before relation assignment.

---

## Related Patterns

This pattern is commonly used with:

* [Get-or-Create Upsert](get-or-create-upsert.md)
* [Derived Record Ensure](derived-record-ensure.md)
* [Idempotent Archive Upsert](idempotent-archive-upsert.md)
* [Immutable Field Guard](immutable-field-guard.md)
