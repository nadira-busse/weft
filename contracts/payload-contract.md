# Payload Contract

This document describes the request and response boundaries used by Weft archive and retrieval workflows.

A payload contract defines what a client may send and what a workflow may return.

```text
client input
↓
workflow boundary
↓
orchestration behavior
↓
storage implementation
```

Machine-checkable validation rules are documented in [`../schemas/`](../schemas/).
Example payloads are documented in [`../examples/public-contracts/`](../examples/public-contracts/).

These contracts do not control every internal behavior of Make or Notion, which retain their own platform constraints.

---

## Contract Set

Weft documents three request and response contract pairs.

| Workflow | Purpose | Request schema | Response schema |
| --- | --- | --- | --- |
| Archive Conversation | Capture an interaction or workflow output as an archive record | [`conversation-archive-request.schema.json`](../schemas/archive/conversation-archive-request.schema.json) | [`conversation-archive-response.schema.json`](../schemas/archive/conversation-archive-response.schema.json) |
| Search Archive | Search archived records through defined filters | [`search-archive-request.schema.json`](../schemas/search/search-archive-request.schema.json) | [`search-archive-response.schema.json`](../schemas/search/search-archive-response.schema.json) |
| Get Context | Retrieve archived content for continued work | [`get-context-request.schema.json`](../schemas/context/get-context-request.schema.json) | [`get-context-response.schema.json`](../schemas/context/get-context-response.schema.json) |

The archive request schema also references the reusable [`message.schema.json`](../schemas/archive/message.schema.json).

Corresponding request and response examples are available in [`../examples/public-contracts/`](../examples/public-contracts/).

---

## Archive Conversation Contract

The archive conversation contract captures a logical interaction as a structured archive payload.

A public archive request can include:

* stable conversation identifier
* human-readable title
* project context
* extraction type
* start and end timestamps
* message count
* ordered messages
* optional source metadata

The stable conversation identifier acts as the primary idempotency key for the archive workflow.

This allows retries or repeated workflow calls to converge on the same logical archive record when the workflow uses an existence-first write model.

The archive response confirms what happened after the archive request was accepted and stored. It does not repeat the full archived content.

---

## Shared Retrieval Request Rules

Both `search_archive` and `get_context` accept these retrieval criteria:

* conversation ID
* project
* query
* date range

Both requests also support a `limit` field to control the maximum number of returned results.

When `date_from` and `date_to` are equal, the request is treated as an exact-date operation.

Requests are rejected when `date_from` is later than `date_to`.

---

## Search Archive Contract

The search archive contract returns record summaries that match the supplied filters.

It is used to discover candidate archive records and does not return the full archived content.

---

## Get Context Contract

The get context contract returns stored archive content for continued work.

The `limit` field has a maximum value of 20.

The response follows the working system shape: retrieved Notion page text is returned as ordered `clean_text` items. Some `clean_text` items may be empty because they reflect empty or structural Notion blocks.

This block-based response shape is intentional. Weft stores long archive content across Notion page blocks because Notion property text storage is limited. The `get_context` workflow retrieves those stored blocks and returns them as ordered `clean_text` items, so longer archived content remains accessible.

Example content may be shortened for readability.
