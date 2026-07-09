# Pattern: Get-or-Create Upsert

## Problem

A workflow must reference a record that may or may not already exist.

For each stable deterministic key, the system should resolve to one logical record.

If the record does not exist, the workflow may need to create it before continuing.

If the workflow always creates a new record, duplicates accumulate over time.

This can lead to:

* duplicate records
* missing references
* inconsistent relationships
* unstable retry behavior

---

## Context

This pattern applies when a workflow must guarantee the existence of a record before continuing.

Common scenarios include:

* relation mapping
* archive systems
* derived record generation
* configuration retrieval
* project or daily-log resolution

---

## Cause

In the Weft implementation, create and update behavior is handled explicitly instead of relying on a native upsert operation.

As a result, workflows must explicitly:

1. determine whether a record exists
2. create it only if it does not
3. reuse the existing record when it does

Upsert behavior is often assumed but not enforced.

---

## Solution

Use an existence-first upsert strategy based on a stable deterministic key.

The system must:

* derive a stable key before any write operation
* use that key for lookup
* branch explicitly on lookup cardinality
* create only after a confirmed zero-result lookup
* resolve one system-generated identifier for downstream use

Routing:

| Lookup outcome     | Required behavior                    |
| ------------------ | ------------------------------------ |
| Error              | Stop or route to error handling      |
| Zero results       | Create record and capture identifier |
| Exactly one result | Reuse existing record                |
| Multiple results   | Fail or resolve ambiguity explicitly |

This creates a single-record guarantee for the deterministic key.

---

## Implementation

A typical implementation follows this flow:

```text
derive deterministic key
↓
lookup by key
↓
route by cardinality
↓
create only if zero results
↓
resolve one identifier
↓
continue downstream
```

All downstream logic must use the resolved identifier.

No implicit execution path should exist after lookup.

---

## Guarantees

When correctly implemented, this pattern helps ensure:

* one logical record per deterministic key
* no duplicate creation under normal retry conditions
* stable references across workflows
* deterministic create vs reuse behavior
* explicit handling of ambiguous matches
* stable key-to-record mapping over time

---

## When to Apply

Use this pattern when:

* a workflow depends on the existence of a record
* records must not be duplicated
* relationships must remain stable
* workflows may be retried or partially executed
* the platform does not provide a safe native upsert

---

## Failure Modes

Without this pattern, systems commonly produce:

* duplicate records
* unresolved references
* broken relationships
* inconsistent system state under retries
* ambiguous matches treated as valid
* multiple records created for the same logical key
* key instability leading to duplicate logical entities

---

## Platform Notes

In systems such as Make + Notion:

* native upsert behavior is not assumed
* lookup results must be handled explicitly
* execution may retry or partially fail
* stable identifiers are needed to prevent duplication

These constraints require explicit existence-first handling.

---

## Related Patterns

This pattern is commonly used with:

* [Explicit Existence Check](explicit-existence-check.md)
* [Input Validation vs Lookup](input-validation-vs-lookup.md)
* [Derived Record Ensure](derived-record-ensure.md)
* [Immutable Field Guard](immutable-field-guard.md)
