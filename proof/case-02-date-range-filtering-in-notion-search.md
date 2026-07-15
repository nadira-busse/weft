# Case 02 — Date Range Filtering in Notion Search

## Context

This case documents how date range filtering in the `search_archive` flow was corrected under Make + Notion execution behavior.

The issue was not simply how to filter by date. The real problem was making date-bounded search behave predictably when date inputs are optional and date filters are sensitive to operator choice, empty values and time boundaries.

The correction had to account for:

* Notion date operator semantics
* Make route and filter behavior
* optional `date_from` and `date_to` inputs
* explicit lower and upper date boundaries

---

## Why This Case Matters

Small mapping or filter mistakes can return records outside the requested date range.

That failure is easy to miss because the response still looks valid, even though the search boundary has been violated.

---

## Runtime Problem

The original date range behavior produced unstable or overly broad result sets.

Observed failure modes included:

* OR logic between date filters leaking too many records
* end-date behavior including records outside the intended day boundary
* empty `date_from` or `date_to` values destabilizing the filter path

---

## Root Cause

Three mechanisms caused the issue.

### 1. OR logic instead of AND logic

If the effective condition becomes:

```text
Start_time >= date_from
OR
Start_time <= date_to
```

then almost the entire archive can match.

Anything satisfying either half is returned. That destroys the intended search boundary.

### 2. Ambiguous end-date behavior

Using an upper-bound date without explicit day-boundary handling can make the end of the range ambiguous.

For same-day searches, this can cause missing results or adjacent-day leakage depending on how the date is interpreted.

### 3. Missing fallback handling

`date_from` and `date_to` are optional.

If empty values are passed directly into Make or Notion filters, the route can fail validation or behave unpredictably.

---

## Correction

The corrected pattern uses a dedicated date-filter route and two explicit date boundaries.

### Route activation

```text
date_from exists OR date_to exists
```

The date route only activates when at least one date boundary is provided.

### Filter logic

The filters are combined with:

```text
AND
```

### Lower bound

```text
Start_time On or after:
ifempty(date_from; archive_baseline)
```

### Upper bound

```text
Start_time On or before:
ifempty(date_to; fallback_upper_date) + explicit end-of-day timestamp
```
The timestamp must use a consistent timezone, because Notion date-time comparisons are timezone-sensitive when time is included.

This makes one-sided and same-day searches explicit instead of relying on implicit platform behavior.

---

## Edge Cases Covered

| Input                   | Expected behavior                                                                            |
| ----------------------- | -------------------------------------------------------------------------------------------- |
| `date_from` only        | Search starts at the requested lower boundary and remains bounded by fallback upper handling |
| `date_to` only          | Search starts from the archive baseline and ends at the requested day                        |
| `date_from` + `date_to` | Search is constrained to the requested date range                                            |
| Same-day search         | Search returns only records within the requested day                                                     |
| Both empty              | Date route does not apply, or fallback behavior remains explicit                             |

---

## Anti-Patterns

| Anti-pattern                                        | Why it fails                                       |
| --------------------------------------------------- | -------------------------------------------------- |
| `Start_time >= date_from OR Start_time <= date_to`  | Leaks records outside the intended range           |
| Implicit upper date boundary                        | Creates ambiguity around end-of-day behavior       |
| Passing empty optional values directly into filters | Can cause validation failure or unstable execution |

---

## Minimal Test Expectation

For a date-bounded search, the response must satisfy:

* records before `date_from` are excluded
* records after `date_to` are excluded
* same-day search returns only records from that day
* empty optional date fields do not break the route
* date filtering does not broaden into unrelated archive results

---

## Reusable Pattern

```text
For bounded date search in Make + Notion,
use explicit lower and upper bounds with AND logic,
apply fallback values to optional inputs,
and normalize the upper date boundary explicitly.
```

---

## Evidence

This case shows that date filtering is enforced at the search boundary through explicit lower and upper bounds.

The correction was applied in the query logic, rather than filtering incorrect results after the search.
