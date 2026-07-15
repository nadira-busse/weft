# Proof

This directory contains runtime evidence from the working Weft implementation.

The cases document concrete problems found during execution with Make and Notion, including the cause, correction and resulting behavior.

---

## Included Cases

| Case                                                              | Focus                                                                     | File                                                                                                                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Case 01 — Search Archive Contract Stabilization                   | Converting raw Notion output into a stable public response shape          | [`case-01-search-archive-contract-stabilization.md`](./case-01-search-archive-contract-stabilization.md)                               |
| Case 02 — Date Range Filtering in Notion Search                   | Correcting date-bounded search behavior under Make and Notion filter      | [`case-02-date-range-filtering-in-notion-search.md`](./case-02-date-range-filtering-in-notion-search.md)                               |
| Case 03 — Single Result Leak After Search                         | Preventing a multi-result search from returning only one result           | [`case-03-single-result-leak-after-search.md`](./case-03-single-result-leak-after-search.md)                                           |
| Case 04 — Notion Relation Array Iterator Mapping with `.value.id` | Handling Notion relation arrays correctly through Make Iterator mechanics | [`case-04-notion-relation-array-iterator-mapping-with-value-id.md`](./case-04-notion-relation-array-iterator-mapping-with-value-id.md) |

The cases are ordered from public contract behavior to deeper Make and Notion runtime behavior.

---

## What These Cases Prove

Together, the cases show that:

* workflow output is deliberately shaped before it is returned
* search behavior is tested against actual Make and Notion behavior
* iterator and bundle handling is made explicit, not assumed
* stored records and workflow responses are kept deliberately separate
* runtime errors and edge cases are investigated and corrected
* predictable behavior depends on explicit checks, not assumptions

---

## Related Documentation

| Directory                                                        | Role                                                            |
| ---------------------------------------------------------------- | --------------------------------------------------------------- |
| [`../architecture/`](../architecture/)                           | Explains the architecture and responsibility boundaries         |
| [`../contracts/`](../contracts/)                                 | Explains the public payload boundaries                          |
| [`../schemas/`](../schemas/)                                     | Defines validation for public request and response shapes       |
| [`../examples/public-contracts/`](../examples/public-contracts/) | Shows example payloads                                          |
| [`../patterns/`](../patterns/)                                   | Captures reusable workflow patterns found during implementation |
