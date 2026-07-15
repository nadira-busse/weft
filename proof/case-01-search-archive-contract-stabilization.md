# Case 01 — Search Archive Contract Stabilization

## Context

This case documents how the `search_archive` flow was corrected from unstable Make + Notion output into a stable search response contract.

The issue was not that search itself failed. The deeper problem was that the workflow exposed internal runtime shape instead of returning one explicit response shape.

That created several problems:

* malformed or incomplete JSON-like output
* `results_count` showing matches while `results` was empty or invalid
* single-result output despite multiple archive matches
* raw Notion `properties_value` structures leaking into the response
* duplicated metadata across `results[]` and top-level `meta`
* ambiguity between `status: "ok"` and `success: true`

---

## Why This Case Matters

`search_archive` is a selection flow. It should return bounded candidate records, not full archive content or raw Notion structures.

The response sometimes showed one result while Notion contained several matches. I only found this by comparing the scenario run history with the records returned by Notion.

---

## Root Cause

The decisive issue was the Array Aggregator configuration.

The wrong target structure had been selected. Instead of aggregating mapped result items into the final response contract, the flow was aggregating into an older or incompatible structure.

This caused:

* raw field leakage
* shape mismatch
* unstable array output
* single-result degradation
* inconsistent response structure

The fix was:

```text
Target structure = Return Output contract
```

This aligned aggregation with the final response shape.

---

## Correction

The corrected flow became:

```text
Search Objects
→ map each result into candidate shape
→ Array Aggregator
→ Return Output
```

The candidate response shape was constrained to:

```json
{
  "id": "...",
  "title": "...",
  "project": "...",
  "summary": "...",
  "model_origin": "...",
  "conversation_id": "..."
}
```

This keeps search output:

* compact
* bounded
* stable
* independent from raw Notion internals

---

## Contract Decision

The success signal was changed from a loose status string to a boolean.

Rejected:

```json
{
  "status": "ok"
}
```

Adopted:

```json
{
  "success": true
}
```

Reason:

* easier to validate
* less wording drift
* clearer for downstream consumers
* separate from descriptive metadata

---

## Final Stable Output

```json
{
  "success": true,
  "results_count": 1,
  "results": [
    {
      "id": "public-example-record-001",
      "title": "Public Summary — Weft",
      "project": "weft",
      "summary": "Public summary of Weft as an archive-first context and knowledge infrastructure project for AI-assisted workflows.",
      "model_origin": "ChatGPT",
      "conversation_id": "2026-06-17_1600_weft_public-summary"
    }
  ],
  "meta": {
    "source": "Notion_Archive_Database",
    "scenario": "search_archive"
  },
  "message": null
}
```

---

## Before / After

| Before                                      | After                                      |
| ------------------------------------------- | ------------------------------------------ |
| Raw `properties_value` structures leaked    | Only approved candidate fields returned    |
| Arrays were malformed or incomplete         | `results[]` is stable                      |
| Multi-result search could return one result | `results_count` and `results.length` align |
| Metadata appeared in multiple places        | Metadata is top-level only                 |
| Status convention drifted                   | `success: true` is the success signal      |

---

## Minimal Test Expectation

For a fixed bounded query, the response must satisfy:

* `success = true`
* `results_count = N`
* `results.length = N`
* each result contains only approved candidate fields
* no raw `properties_value`
* no internal storage blobs
* top-level metadata only
* no duplicated metadata inside results
* `message` is present as string or null

---

## Reusable Pattern

```text
Do not return raw Notion search structures directly.

Map each record into an explicit candidate shape,
aggregate into the final response contract,
and return only the approved public structure.
```

---

## Evidence

This case shows that the final search response is explicitly projected and aggregated before it is returned, not left to whatever Make or Notion happen to return by default.
