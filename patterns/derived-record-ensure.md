# Pattern: Derived Record Ensure

## Problem

Derived records must satisfy a single-instance invariant.

For each stable grouping key, exactly one derived record should exist and remain correctly linked to its primary records.

Typical issues include:

* missing derived records
* duplicate records for the same grouping key
* incorrect or missing relationships
* orphaned records after partial failures
* derived metadata drifting away from source records

---

## Context

This pattern applies when a system creates secondary records from primary events or source records.

Examples include:

* time-based grouping, such as daily or periodic records
* aggregated summaries
* grouped activity records
* derived datasets based on primary events
* helper records used for filtering, reporting or navigation

Derived records support the system. They should not automatically become the source of truth.

---

## Cause

Derived records are often handled with implicit logic such as:

```text id="n7u940"
create if missing
```

This becomes unreliable when:

* write order is not controlled
* retries occur after partial execution
* relations are created before dependencies exist
* grouping logic is not enforced consistently
* derived records are treated as authoritative without validation

Without an explicit ensure strategy, derived data becomes inconsistent over time.

---

## Solution

Use an existence-first ensure strategy after the primary write.

The system must:

* ensure the primary record exists first
* derive a stable grouping key from the primary record
* look up the derived record by that grouping key
* reuse exactly one existing derived record
* create only when no matching derived record exists
* fail or resolve ambiguity when multiple derived records match
* explicitly link the primary and derived records

This preserves relationship consistency and safer retry behavior.

---

## Implementation

A typical implementation follows this flow:

```text id="y3s3ru"
ensure primary record exists
↓
derive stable grouping key
↓
lookup derived record by grouping key
↓
route by cardinality
↓
reuse or create derived record
↓
link primary and derived records
```

Routing:

```text id="jcnry2"
0 records → create derived record and link
1 record  → reuse derived record and link
2+ records → fail or resolve ambiguity
error → error handling
```

All downstream logic must reference the resolved derived record.

---

## Guarantees

When correctly implemented, this pattern helps ensure:

* one derived record per stable grouping key
* stable relationships between primary and derived records
* fewer duplicate or orphaned derived records
* clearer retry behavior after partial execution
* separation between source records and derived helper records

---

## When to Apply

Use this pattern when:

* derived records must exist once per grouping key
* relationships between records must remain consistent
* workflows are retry-prone or non-atomic
* partial failures may occur
* derived records support search, grouping, reporting or navigation

---

## Failure Modes

Without this pattern, systems commonly produce:

* duplicate derived records
* missing derived records
* inconsistent relationships
* orphaned records after partial execution
* race-condition-induced duplicates
* derived records that appear authoritative but are not tied back to source records

---

## Platform Notes

In systems such as Make + Notion:

* lookup operations may return empty results without errors
* explicit routing is required to distinguish existence states
* write order directly affects relational consistency
* relation mapping requires the resolved record identifier

These constraints make an explicit ensure strategy necessary.

---

## Related Patterns

This pattern is commonly used with:

* [Explicit Existence Check](explicit-existence-check.md)
* [Get-or-Create Upsert](get-or-create-upsert.md)
* [Idempotent Archive Upsert](idempotent-archive-upsert.md)
* [Relation Identifier Mapping](relation-identifier-mapping.md)
