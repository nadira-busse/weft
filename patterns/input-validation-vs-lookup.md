# Pattern: Input Validation vs Lookup

## Problem

Workflows often treat missing input values and missing lookup results as the same condition.

They are not the same.

A missing required input is invalid input.

A lookup with zero results is a valid lookup outcome.

If these states are mixed, workflows can make incorrect decisions.

This can lead to:

* valid workflows being rejected
* unnecessary record creation
* ensure logic being bypassed
* invalid inputs passing through
* lookup operations running on incomplete input

---

## Context

This pattern appears in workflows that combine:

* input validation
* record lookups
* conditional creation or linking
* idempotent write logic
* relation resolution

---

## Cause

Two different states are often confused.

### Empty Input

A required input value is missing or undefined.

Example:

```text
project = ""
```

This is a validation failure.

The workflow must not continue to lookup.

### Not Found

A lookup executes successfully but returns no matching records.

Example:

```text
lookup → 0 results
```

This is a valid lookup result.

It means the record does not exist yet, or the search boundary did not match anything.

---

## State Model

The workflow must distinguish between four states:

| State              | Meaning                                   | Required behavior                    |
| ------------------ | ----------------------------------------- | ------------------------------------ |
| Invalid input      | Required value is empty or undefined      | Fail early                           |
| Zero results       | Lookup ran successfully but found nothing | Execute not-found or ensure logic    |
| Exactly one result | Lookup found one valid match              | Continue with resolved record        |
| Multiple results   | Lookup found ambiguous matches            | Fail or resolve ambiguity explicitly |

Each state requires different handling.

---

## Solution

Separate the workflow into two ordered stages:

```text
1. Input validation
2. Record lookup
```

The system must:

* validate required inputs first
* fail immediately on invalid input
* perform lookup only after input is valid
* route lookup results by cardinality
* prevent implicit fallback paths

Validation and lookup must never be combined into one decision point.

---

## Implementation

A typical implementation follows this flow:

```text
validate required input
↓
if invalid → fail early
↓
if valid → perform lookup
↓
route by lookup cardinality
```

Lookup routing:

```text
0 records → create or handle absence explicitly
1 record  → reuse validated record
2+ records → fail or resolve ambiguity
error → error handling
```

All downstream logic must operate on:

* validated input
* resolved lookup result
* explicit routing state

---

## Guarantees

When correctly implemented, this pattern helps ensure:

* no lookup execution on invalid input
* no record creation from invalid input
* clear separation between validation and lookup logic
* deterministic routing based on lookup result
* correct interaction with ensure and upsert patterns

---

## When to Apply

Use this pattern when workflows include:

* lookups based on external input
* conditional record creation
* idempotent write logic
* relation resolution
* required fields that determine downstream routing

---

## Failure Modes

Without this separation, systems commonly produce:

* validation logic mixed with lookup logic
* records created for invalid input
* valid workflows incorrectly blocked
* unpredictable routing behavior
* ambiguous states treated as valid input
* lookup operations executed with invalid input

---

## Platform Notes

In systems such as Make:

* missing input values and empty lookup results are distinct states
* lookup operations may return zero results without errors
* execution can continue unless explicitly controlled

These constraints require validation and lookup to be separated before downstream workflow steps run.

---

## Related Patterns

This pattern is commonly used with:

* [Explicit Existence Check](explicit-existence-check.md)
* [Get-or-Create Upsert](get-or-create-upsert.md)
* [Derived Record Ensure](derived-record-ensure.md)
