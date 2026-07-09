# Weft Engineering Patterns

Reusable engineering patterns found while building Weft.

I documented these patterns because the same reliability problems kept appearing across the archive and retrieval workflows.

The focus is on:

* deterministic behavior
* idempotent operations
* reliable data relationships
* predictable execution under failure

---

## Implementation Context

These patterns originate from the working Weft implementation using:

* Make as orchestration layer
* Notion as archive system of record

They reflect real workflow behavior, including platform constraints such as:

* lookup operations returning empty results instead of errors
* absence of native upsert operations
* dependency on stable identifiers for correctness
* non-atomic execution and retry behavior

The patterns are documented from the Weft implementation context.

---

## Pattern Model

Each pattern describes a recurring problem and its resolution at the architectural level, supported by implementation context where necessary.

Patterns follow a consistent structure:

* **Problem** — the recurring system issue
* **Context** — where the issue appears
* **Cause** — why the issue occurs
* **Solution** — the architectural approach
* **Implementation** — how the solution is realized in practice
* **Platform Notes** — relevant system or tool constraints
* **When to Apply** — situations where the pattern is required
* **Failure Modes** — what happens without the pattern
* **Related Patterns** — complementary patterns

Patterns focus on the design logic behind the workflow, not on step-by-step Make configuration.

---

## Pattern Categories

The patterns in this library address core reliability concerns.

### Lookup & Selection

* handling missing or ambiguous results
* separating “not found” from “invalid input”
* ensuring deterministic selection

### Persistence & Idempotency

* preventing duplicate writes
* enforcing stable identifiers
* controlling create vs update behavior

### Data Integrity

* protecting immutable fields
* maintaining consistent relationships
* enforcing schema constraints

### Derived Data

* ensuring consistency of derived records
* separating source or curated data from computed metadata

---

## Available Patterns

Each pattern is documented in its own file.

### Lookup & Selection

* [Explicit Existence Check](explicit-existence-check.md) — Handle non-error empty lookup results
* [Input Validation vs Lookup](input-validation-vs-lookup.md) — Separate validation from lookup outcomes

### Persistence & Idempotency

* [Get-or-Create Upsert](get-or-create-upsert.md) — Ensure existence without duplication
* [Idempotent Archive Upsert](idempotent-archive-upsert.md) — Prevent duplicate writes under retries

### Data Integrity

* [Immutable Field Guard](immutable-field-guard.md) — Protect write-once identifiers
* [Relation Identifier Mapping](relation-identifier-mapping.md) — Maintain correct cross-entity references

### Derived Data

* [Derived Record Ensure](derived-record-ensure.md) — Ensure consistent derived data

---

## Why This Library Exists

Automation systems often become fragile when important behavior stays implicit.

Common causes include:

* assumptions hidden in lookup logic
* inconsistent write behavior
* unstable identifiers
* unclear ownership between workflow steps
* hidden coupling between components

These patterns help make that behavior explicit.

I do not present these patterns as a full framework. They are reusable notes from a working system, written down so I do not have to solve the same workflow problems from scratch each time.

---

## Relationship to Weft

These patterns support the reliability goals of Weft:

* predictable workflow behavior
* idempotent persistence
* stable archive identity
* traceable execution behavior

They explain why the archive and retrieval workflows are structured the way they are.
