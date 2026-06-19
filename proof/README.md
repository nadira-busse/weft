# Proof

This directory contains public-safe runtime evidence from the working Weft implementation.

The files in this directory show where Weft was tested, corrected and stabilized while running with Make and Notion. They are not architecture notes. They document concrete problems that appeared during execution and how they were fixed.

---

## What This Proof Layer Shows

The proof cases show that Weft is not only described as an architecture. Parts of the system were actually exercised in a working workflow.

The cases document:

* public contract stabilization
* date-bounded search behavior
* multi-result retrieval handling
* Make bundle and iterator behavior
* Notion relation mapping
* separation between internal storage and public workflow output

These are runtime-level problems. They matter because Weft depends on predictable archive, search and retrieval behavior.

---

## Included Cases

| Case                                                              | Focus                                                                     | File                                                                                                                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Case 01 — Search Archive Contract Stabilization                   | Converting raw Notion output into a stable public response shape          | [`case-01-search-archive-contract-stabilization.md`](./case-01-search-archive-contract-stabilization.md)                               |
| Case 02 — Date Range Filtering in Notion Search                   | Correcting date-bounded retrieval under Make and Notion filter behavior   | [`case-02-date-range-filtering-in-notion-search.md`](./case-02-date-range-filtering-in-notion-search.md)                               |
| Case 03 — Single Result Leak After Search                         | Preventing a multi-result search from returning only one result           | [`case-03-single-result-leak-after-search.md`](./case-03-single-result-leak-after-search.md)                                           |
| Case 04 — Notion Relation Array Iterator Mapping with `.value.id` | Handling Notion relation arrays correctly through Make Iterator mechanics | [`case-04-notion-relation-array-iterator-mapping-with-value-id.md`](./case-04-notion-relation-array-iterator-mapping-with-value-id.md) |

---

## What These Cases Prove

Together, these cases show that:

* workflow output is shaped deliberately before it is returned
* search and retrieval behavior is tested against real platform behavior
* internal Notion structures are not exposed as public contracts
* Make iterator and bundle behavior is handled explicitly
* errors and edge cases are corrected instead of hidden
* deterministic behavior is created through checks and corrections, not assumptions

---

## Relationship to the Rest of the Repository

| Directory                                                        | Role                                                               |
| ---------------------------------------------------------------- | ------------------------------------------------------------------ |
| [`../architecture/`](../architecture/)                           | Explains the architecture and responsibility boundaries            |
| [`../contracts/`](../contracts/)                                 | Explains the public payload boundaries                             |
| [`../schemas/`](../schemas/)                                     | Defines validation for public request and response shapes          |
| [`../examples/public-contracts/`](../examples/public-contracts/) | Shows public-safe example payloads                                 |
| [`../patterns/`](../patterns/)                                   | Captures reusable workflow patterns found during implementation    |
| [`../proof/`](../proof/)                                         | Documents runtime corrections and evidence from the working system |

---

## Reading Order

Recommended order:

1. [`case-01-search-archive-contract-stabilization.md`](./case-01-search-archive-contract-stabilization.md)
2. [`case-02-date-range-filtering-in-notion-search.md`](./case-02-date-range-filtering-in-notion-search.md)
3. [`case-03-single-result-leak-after-search.md`](./case-03-single-result-leak-after-search.md)
4. [`case-04-notion-relation-array-iterator-mapping-with-value-id.md`](./case-04-notion-relation-array-iterator-mapping-with-value-id.md)

This order moves from public contract behavior to deeper Make and Notion runtime behavior.

---

## Boundary

This proof layer shows that Weft has been tested and corrected in a working personal workflow.

It does not claim that Weft is a finished product, a SaaS platform or a generally deployable system. The value of this directory is narrower and more concrete: it shows how runtime issues were found, understood and fixed.
