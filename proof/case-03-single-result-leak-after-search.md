# Case 03 — Single Result Leak After Search

## Context

This case documents a Make-specific failure mode in the `search_archive` flow.

The search returned multiple matching records, but the final scenario output exposed only one result.

The issue was not search correctness. It was final response aggregation.

---

## Why This Case Matters

This is the kind of failure that weakens trust quickly.

A system can appear correct while silently dropping valid results. That is especially risky in archive and retrieval systems, where result completeness is part of correctness.

The lesson here is specific to Make: bundle behavior has to be handled explicitly. Assuming multiple records will automatically combine into one response array is exactly what caused this bug.

---

## Runtime Problem

The Notion Search step returned multiple valid matches.

However, the final scenario output exposed only one result.

This happened despite:

* correct filtering
* correct search execution
* multiple valid records
* an apparently valid response structure

The system therefore looked correct while silently returning only one bundle in the final output.

---

## Root Cause

The root cause was missing final aggregation.

In Make:

* Search can emit multiple bundles
* downstream mapping can also execute per bundle
* Return Output does not automatically combine those bundles into one response array

Without explicit aggregation, a multi-result search can degrade into single-result output.

This is a bundling problem, not a search problem.

---

## Incorrect Execution Shape

The failing shape was:

```text
Search
→ per-result mapping
→ Return Output
```

What happens:

* Search emits multiple bundles
* each bundle is mapped independently
* Return Output receives bundle-level data, not a finalized array
* only one mapped result effectively appears in the response

---

## Correction

The corrected flow is:

```text
Search
→ per-result mapping
→ Array Aggregator
→ Return Output
```

The Array Aggregator:

* consumes all matching bundles
* combines them into one ordered result array
* emits one bundle
* gives Return Output a stable payload source

That matches the public contract expectation:

```text
many records found
→ one response
→ one explicit results array
```

---

## Before / After

| Before                                | After                                                    |
| ------------------------------------- | -------------------------------------------------------- |
| `Search → map result → Return Output` | `Search → map result → Array Aggregator → Return Output` |
| Search finds many                     | Search finds many                                        |
| Output returns one                    | Output returns many                                      |
| Result completeness is accidental     | Result completeness is explicit                          |

---

## Anti-Patterns

| Anti-pattern                                               | Why it fails                                                      |
| ---------------------------------------------------------- | ----------------------------------------------------------------- |
| Assuming Search returns an array                           | Search emits multiple bundles, not one finalized response object  |
| Assuming Return Output aggregates bundles                  | Return Output emits what it receives                              |
| Treating per-result mapping as final response construction | Per-bundle transformation is not contract-level response assembly |

---

## Minimal Detection Rule

```text
If Search shows multiple bundles in run history
but the final response contains one result,
final aggregation is missing.
```

---

## Response Contract Expectation

For a successful multi-result search:

```text
results_count = N
results.length = N
```

The response must not silently drop valid search candidates.

---

## Reusable Pattern

```text
Whenever a Make scenario must return multiple records,
aggregate explicitly before Return Output.

Do not rely on Search or Return Output to combine bundles implicitly.
```

---

## What This Proves

What this case is evidence of:

* understanding of Make bundle semantics
* separation between per-bundle mapping and final response construction
* explicit control over multi-result output
* prevention of silent data loss in retrieval
* contract-level assembly before returning the response

The reason this is worth documenting: the failure is easy to miss. The workflow can look correct while quietly returning incomplete results.
