# Weft Engineering Patterns

This library documents reusable engineering patterns that emerged while building Weft.

The same reliability problems kept appearing across the archive and retrieval workflows, especially around lookup behavior, idempotency, stable identity and data relationships.

---

## Implementation Context

The patterns come from the working Weft implementation, which uses Make for orchestration and Notion as the archive system of record.

They address platform behavior such as:

* lookup operations returning empty results instead of errors
* absence of native upsert operations
* dependency on stable identifiers
* non-atomic execution and retry behavior

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

---
## Available Patterns

### Lookup & Selection

Patterns for handling missing or ambiguous results and separating validation from lookup outcomes.

* [Explicit Existence Check](explicit-existence-check.md) — Handle non-error empty lookup results
* [Input Validation vs Lookup](input-validation-vs-lookup.md) — Separate validation errors from valid lookup outcomes

### Persistence & Idempotency

Patterns for preventing duplicate writes and controlling create-versus-update behavior.

* [Get-or-Create Upsert](get-or-create-upsert.md) — Ensure existence without duplication
* [Idempotent Archive Upsert](idempotent-archive-upsert.md) — Prevent duplicate writes under retries

### Data Integrity

Patterns for protecting stable identity and maintaining correct relationships.

* [Immutable Field Guard](immutable-field-guard.md) — Protect write-once identifiers
* [Relation Identifier Mapping](relation-identifier-mapping.md) — Maintain correct cross-entity references

### Derived Data

Patterns for keeping derived records consistent with their source data.

* [Derived Record Ensure](derived-record-ensure.md) — Ensure required derived records exist consistently

---
## Scope

This is not a complete automation framework.

It is a set of reusable patterns from a working system, documented so the same workflow problems do not have to be solved from scratch each time.
