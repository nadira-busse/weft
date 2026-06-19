# Pattern: Explicit Existence Check

## Problem

Lookup operations may return no results without failing.

A workflow must not assume that “not found” is an error, or that a successful lookup always means one valid record exists.

Lookup results must be treated as four possible outcomes:

* operation error
* zero results
* exactly one result
* multiple results

Without explicit handling, workflows can make incorrect routing decisions.

This can lead to:

* updates against non-existent records
* unintended record creation
* ambiguous matches being treated as valid
* unpredictable workflow behavior

---

## Context

This pattern applies to workflows that use lookup operations to determine whether a record exists before continuing.

Typical scenarios include:

* checking whether a record already exists
* resolving relations before write operations
* deciding whether to create or update a record
* ensuring a related or derived record exists

---

## Cause

Some platforms treat “no result” as a valid lookup outcome rather than an execution error.

That means the workflow may continue even though no record was found.

If the workflow does not branch explicitly, downstream steps may operate on an unresolved or invalid state.

---

## Solution

Use an explicit existence check immediately after every lookup operation.

Route based on result cardinality:

| Lookup outcome     | Required behavior                    |
| ------------------ | ------------------------------------ |
| Error              | Stop or route to error handling      |
| Zero results       | Execute not-found logic              |
| Exactly one result | Continue with the validated record   |
| Multiple results   | Fail or resolve ambiguity explicitly |

No implicit execution path should exist after a lookup.

All downstream logic must operate on a resolved and validated record state.

---

## Implementation

A typical implementation follows this flow:

```text
lookup
↓
evaluate result cardinality
↓
route explicitly
↓
continue only with resolved state
```

For create/update workflows, this usually means:

```text
0 records → create
1 record  → update or reuse
2+ records → fail or resolve ambiguity
error → error handling
```

---

## Guarantees

When correctly implemented, this pattern helps ensure:

* clear distinction between “not found” and failure
* deterministic routing based on lookup results
* no updates against non-existent records
* consistent create vs update behavior
* explicit handling of ambiguous matches
* no hidden fallback path after lookup

---

## When to Apply

Use this pattern when:

* workflows depend on lookup results
* record existence determines execution flow
* create vs update decisions are required
* relation resolution is required before writing
* the platform does not throw errors for “not found”

---

## Failure Modes

Without this pattern, systems commonly produce:

* updates against missing records
* duplicate records
* broken ensure logic
* unpredictable execution paths
* silent logical errors due to implicit assumptions
* ambiguous matches silently treated as valid

---

## Platform Notes

In systems such as Make:

* lookup modules may return empty results without errors
* execution can continue unless explicitly branched
* “not found” must be handled as a separate state

These constraints require explicit handling of empty results before downstream steps run.

---

## Related Patterns

This pattern is commonly used with:

* [Get-or-Create Upsert](get-or-create-upsert.md)
* [Idempotent Archive Upsert](idempotent-archive-upsert.md)
* [Derived Record Ensure](derived-record-ensure.md)
* [Input Validation vs Lookup](input-validation-vs-lookup.md)
