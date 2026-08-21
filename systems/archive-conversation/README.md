# Archive Conversation

Archive Conversation is Weft's write path. It receives a structured conversation from an MCP-enabled client, normalizes and validates the input, and stores the result as an Archive record in Notion.

The workflow also maintains the relationship between an Archive, its Project and the relevant Daily Log. This document explains how that write path works, how an existing conversation is identified, and when Weft updates, repairs or rejects a request.

What began as a workflow for storing conversations became more complicated once the same conversation could be archived again. A repeated request should update the existing Archive, while a request that assigns the same conversation to another project must be rejected without changing stored state.

[Inspect `archive_conversation` in Make](https://eu1.make.com/public/shared-scenario/UrKrdWWmdo8/weft-archive-conversation)

The exported blueprint is stored at [`setup/Make/blueprints/weft_archive_conversation.json`](../../setup/Make/blueprints/weft_archive_conversation.json).

## The write boundary

The implemented order is:

```text
input

→ normalize conversation ID, timestamps and metadata

→ validate normalized values

→ assemble transcript and storage payload

→ resolve Daily Log and Project records

→ check the stored conversation and project identity

→ create, update or repair only on an allowed route

→ append the persisted page content

→ return the response
```

Normalization happens before any Notion operation.

Normalization trims `conversation_id`; a whitespace-only value therefore returns `validation_error` without a Notion lookup or write.

Datetimes are also converted before validation instead of requiring every accepted client representation to already use the stored datetime format.

The request and response fields are defined in the [payload contract](../../contracts/payload-contract.md), [JSON Schemas](../../schemas/archive-conversation/) and [sanitized fixtures](../../examples/contracts/archive-conversation/). This document describes the write behavior behind those payloads rather than repeating the contract.

## One conversation, one project identity

`conversation_id` is the stable Archive identity.

A new ID takes the create route. A repeated accepted request finds the existing Archive and takes the update route, so both requests use the same record.

That reuse is allowed only while the normalized project key still matches the stored key.

A request that tries to bind the same conversation to another project returns `PROJECT_CONFLICT`. On that route, the scenario does not create or update a Project, Archive, page content or Error Log record. The existing Archive identity is returned so the caller can see which record caused the conflict.

A missing Project record is handled separately from a conflict.

If an Archive already contains the same project key but no longer has a valid Project relation, the repair route recreates the Project once and attaches the existing Archive to it. It does not create another Archive merely because the related Project record disappeared.

Repeating an accepted archive request with the same `conversation_id` reuses the existing Archive record instead of creating another one. Existing page content is not overwritten: content from the new request is appended below it. Weft does not currently detect whether those appended blocks duplicate content that is already present.

## What failed around datetime handling

The input accepts either an ISO 8601 datetime or a local `HH:mm` value.

The first implementation treated those forms inconsistently:

* A value such as `06:00` reached Make's date parser without a calendar date.
* After parsing was corrected, validation still inspected the raw client value and rejected a supported `HH:mm` input.
* An explicit `end_time` could be replaced by the later workflow execution time.
* One attempted mapping depended on another output from the same Make module, even though that output did not exist until the module completed.
* The installation timezone appeared in several expressions, leaving more than one place to change it.

The corrected path builds a complete local datetime before parsing, validates the normalized result and preserves a supplied `end_time`.

Only a missing end time uses the current archive time.

An upstream `weft_timezone` variable supplies the installation timezone to normalization and Daily Log date derivation. The supplied blueprint sets this value to `Europe/Amsterdam`.

The `Europe/Amsterdam` configuration was runtime-tested, including the normalization assertions recorded in the V4 regression run. Equivalent runtime testing has not been performed for every other IANA timezone.

There is also an information boundary the workflow cannot repair. `06:00` contains no historical date. When a conversation is archived on a later day, the caller must provide at least a dated `start_time`; an `HH:mm` end time can then inherit that known date.

## Evidence and limits

The [V4 regression report](../../regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md) records the responses and Notion assertions tested for seven Archive routes on 6 August 2026. Those results apply to the behavior tested in that regression run.

The stored [Make run-history screenshot](./assets/screenshots/make-archive-conversation-run-history.png) and [Notion Archive screenshot](./assets/screenshots/notion-archive-db-evidence-view.png) are representative runtime evidence. They show that the workflow ran and persisted records; screenshots alone do not prove every regression route.

Archive requests containing Markdown-formatted `python -m ...` commands can receive HTTP 403 before this scenario starts. The reproduced behavior and workaround are documented in the [Make MCP troubleshooting note](./troubleshooting/make-mcp-403-markdown-python-module-command.md).

Current installation and platform boundaries are documented in [Known limitations](../../setup/known-limitations.md).
