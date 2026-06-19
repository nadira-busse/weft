# Case 04 — Notion Relation Array Iterator Mapping with `.value.id`

## Context

This case documents a Make + Notion integration problem in relation traversal.

Iterating over a Notion relation field produced two failures:

* invalid Page ID errors
* incomplete iteration over related records

The correction required understanding the runtime shape of Notion relation properties and how Make handles arrays before and inside an Iterator.

---

## Why This Case Matters

Relation traversal often supports downstream reconstruction, grouping or linked-record retrieval.

If relation arrays are mapped incorrectly, the workflow may fail with invalid ID errors or silently retrieve only one related record.

That matters for Weft because retrieval depends on complete and predictable traversal of stored context.

---

## Runtime Problem

Two failures appeared while iterating over a Notion relation property and retrieving related records.

### Problem 1 — Invalid Page ID

A Notion Get step received an invalid page identifier and raised an error equivalent to:

```text id="lqzd3b"
path.page_id should be a valid uuid, instead was {"value":"..."}
```

### Problem 2 — Incomplete Iteration

The Iterator processed only one bundle even though the relation contained multiple entries.

That made traversal incomplete and unreliable.

---

## Root Cause

A Notion relation property is not an array of UUID strings.

It is an array of objects:

```json id="8reqhj"
[
  { "id": "00000000-0000-0000-0000-000000000001" },
  { "id": "00000000-0000-0000-0000-000000000002" }
]
```

That creates two separate mapping rules.

### Before the Iterator

The full relation array must be passed into the Iterator.

Use:

```text id="j1didt"
relation_field[]
```

Without array notation, Make may pass only the first relation entry.

### Inside the Iterator

The current item is already one relation object.

Use:

```text id="8me4gq"
N.value.id
```

This extracts the UUID string expected by Notion.

Do not use:

```text id="ctt83h"
N.value
```

as a Page ID when the current item is a relation object. That passes the whole object instead of the UUID string.

---

## Correct Implementation Pattern

```text id="5i3ylu"
Iterator input:
relation_field[]

Notion Get Page ID inside the Iterator:
N.value.id
```

This combination solves both problems:

* the Iterator receives all related records
* the Notion Get step receives a valid UUID string

---

## Anti-Patterns

| Anti-pattern                                | Why it fails                                                |
| ------------------------------------------- | ----------------------------------------------------------- |
| Using `N.value` as Page ID                  | Passes the whole relation object instead of the UUID string |
| Using array notation inside the Iterator    | The current bundle is already one item                      |
| Omitting array notation before the Iterator | The Iterator may process only the first relation entry      |

---

## Iterator Mapping Reference

Iterator mapping depends on the type of array being processed.

| Array type            | Correct access pattern |
| --------------------- | ---------------------- |
| String array          | `N.value`              |
| Relation object array | `N.value.id`           |
| Generic object array  | `N.value.field_name`   |

This distinction matters because Make does not automatically flatten object arrays into the exact field a downstream module expects.

---

## Minimal Test Expectation

For a relation field with multiple related records, the workflow must satisfy:

* the Iterator receives the full relation array
* each relation entry is processed
* each Notion Get step receives a UUID string
* no Page ID receives the full relation object
* traversal does not silently stop after the first relation entry

---

## Reusable Pattern

```text id="x4t3ql"
When iterating over a Notion relation field in Make,
pass the full relation array into the Iterator,
and inside the Iterator access the UUID via .value.id.
```

---

## What This Proves

What this confirms: Weft's retrieval behavior is grounded in how the data actually looks at runtime, not in how it's assumed to look.

It shows:

* correct interpretation of Notion relation properties
* correct use of Make Iterator mechanics
* explicit treatment of object arrays versus string arrays
* correction of incomplete iteration
* correction of invalid Page ID mapping

Relation traversal can fail in ways that are hard to notice. This case is worth documenting because the failure was traced back to its real cause — the actual shape of the data — and fixed there, instead of being patched around.
