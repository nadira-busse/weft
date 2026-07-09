# Payload Contract

## Overview

This document describes the public payload boundaries used by Weft archive and retrieval workflows.

A payload contract defines what a client may send to a workflow and what the workflow may return.

In Weft, contracts sit between:

```text
client input
↓
workflow boundary
↓
orchestration behavior
↓
storage implementation
```

The purpose is to make workflow behavior easier to inspect, validate and correct.

Machine-checkable validation rules are documented in [`../schemas/`](../schemas/).
Example payloads are documented in [`../examples/public-contracts/`](../examples/public-contracts/).

---

## Public Boundary

This repository documents the workflow boundary, not the full internal implementation.

It shows:

* request and response shapes
* validation expectations
* example payloads
* workflow behavior at the contract level

It does not publish private archive content, internal IDs, URLs, database structures or Make scenario internals.

---

## Contract Families

Weft currently documents three public contract families.

| Contract             | Purpose                                                        |
| -------------------- | -------------------------------------------------------------- |
| Archive Conversation | Capture an interaction or workflow output as an archive record |
| Search Archive       | Search archived records through defined filters                |
| Get Context          | Retrieve archived context for continued work                   |

Each contract has:

* a conceptual description in this document
* request and/or response schemas in [`../schemas/`](../schemas/)
* examples in [`../examples/public-contracts/`](../examples/public-contracts/)

Request and response contracts are documented separately where needed. A request describes what the workflow accepts. A response describes what the workflow returns.

---

## Schema Files

Current public schema files:

| Workflow             | Request schema                                                                                                               | Response schema                                                                                                                |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Archive Conversation | [`../schemas/archive/conversation-archive-request.schema.json`](../schemas/archive/conversation-archive-request.schema.json) | [`../schemas/archive/conversation-archive-response.schema.json`](../schemas/archive/conversation-archive-response.schema.json) |
| Search Archive       | [`../schemas/search/search-archive-request.schema.json`](../schemas/search/search-archive-request.schema.json)               | [`../schemas/search/search-archive-response.schema.json`](../schemas/search/search-archive-response.schema.json)               |
| Get Context          | [`../schemas/context/get-context-request.schema.json`](../schemas/context/get-context-request.schema.json)                   | [`../schemas/context/get-context-response.schema.json`](../schemas/context/get-context-response.schema.json)                   |

The archive request schema also uses the reusable message schema:

```text
../schemas/archive/message.schema.json
```

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
* message order preservation
* optional source metadata

The stable identifier is the primary idempotency key.

This allows retries or repeated workflow calls to converge on the same logical archive record when the workflow uses an existence-first write model.

The archive response confirms what happened after the archive request was accepted and stored. It does not repeat the full archived content.

---

## Search Archive Contract

The search archive contract finds archive records through explicit search inputs.

Supported public filters include:

* conversation ID
* project
* query
* date range
* result limit

When `date_from` and `date_to` are equal, the workflow treats the request as an exact-date search.

The workflow rejects date-range requests where `date_from` is later than `date_to`.

Search outputs return record summaries, not full archive content.

---

## Get Context Contract

The get context contract retrieves archived content for continued work.

A public get-context request can use:

* conversation ID
* project
* query
* date range
* result limit

When `date_from` and `date_to` are equal, the workflow treats the request as an exact-date retrieval.

Date-range requests are rejected when `date_from` is later than `date_to`.

The `limit` field is accepted by the public input boundary with a maximum of 20.

The response follows the working system shape: retrieved Notion page text is returned as ordered `clean_text` items. Some `clean_text` items may be empty because they reflect empty or structural Notion blocks.

This block-based response shape is intentional. Weft stores long archive content across Notion page blocks because Notion property text storage is limited. The `get_context` workflow reconstructs those stored blocks so longer archived content can still be retrieved later.

Example content may be shortened for readability.

---

## Write and Retrieval Behavior

Payload contracts help keep workflow behavior predictable.

For archive workflows, this depends on:

* stable identifiers
* required fields
* message order preservation
* existence-first checks
* controlled create/update behavior

For retrieval workflows, this depends on:

* explicit filters
* predictable response shapes
* clear distinction between validation errors and valid zero-result searches

This does not mean every internal platform behavior is controlled by the contract.

The contract defines the public boundary. Make and Notion still have their own platform constraints.

---

## Architectural Role

The payload contract is the boundary between temporary AI/workflow output and persistent archive behavior.

ChatGPT, Claude, MCP-enabled workflows, webhooks or other clients can send structured input without owning the archive state.

The archive remains the source of record.
