# Case 02 - Date Filtering in Notion Search

## Context

`search_archive` has two date routes in the exported blueprint:

- exact date when `date_from == date_to`;
- inclusive date range when both fields exist and are not equal.

The public request contract requires both date fields. One-sided dates are not documented as valid routes.

## Failure mode

Date filters can look structurally valid while returning records outside the requested boundary. The two common causes are combining lower and upper bounds with OR semantics and treating a date-only upper bound as an unspecified timestamp.

## Exported correction

The range route in `weft_search_archive.json`, module 55, applies both conditions in one filter group:

```text
Start time on or after date_from
AND
Start time on or before end-of-day(date_to)
```

The upper bound parses `date_to` in `Europe/Amsterdam`, adds one day, subtracts one second, and formats the resulting timestamp. The exact-date route in module 50 instead uses Notion's date-equals operator.

## Contract expectation

| Input | Route |
|---|---|
| equal `date_from` and `date_to` | exact date |
| ascending `date_from` and `date_to` | inclusive date range |
| descending values | validation response with `success: false` |
| only one date field | invalid public request |

For a bounded search, records before `date_from` and after the end of `date_to` must be excluded. The response remains a structured `results` array with `results_count` matching the aggregate length.

## Evidence boundary

The accepted ChatGPT-client date test returned the two expected records with all public result fields. The canonical blueprint provides static evidence for the filters and timezone calculation; this document is not an API read-back log and does not prove a fresh installation.
