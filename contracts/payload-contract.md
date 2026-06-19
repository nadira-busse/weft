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

The purpose is to make workflow behavior easier to inspect, validate and correct without exposing the private Make or Notion implementation.

Machine-checkable validation rules are documented in [`../schemas/`](../schemas/).
Public-safe example payloads are documented in [`../examples/public-contracts/`](../examples/public-contracts/).

---

## Scope

This contract describes the public boundary of Weft workflows.

It does not publish:

* private Notion database structures
* Make scenario internals
* internal relation-property names
* private IDs or URLs
* private raw archive content
* complete production variants

The public contract is intentionally smaller than the internal implementation.

Public examples may include intentionally public project content when that content helps show workflow behavior.

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
* public-safe examples in [`../examples/public-contracts/`](../examples/public-contracts/)

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
* ordered messages
* optional source metadata

The stable identifier is the primary idempotency key.

This allows retries or repeated workflow calls to converge on the same logical archive record when the workflow uses an existence-first write model.

The public archive response confirms what happened after the archive request was accepted and stored. It does not repeat the full archived content.

Private implementation details are intentionally omitted.

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

Search outputs return public-safe record summaries, not full private archive records.

This keeps the contract useful without exposing internal storage details.

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

Long public content may be shortened in examples for readability. Private content, internal IDs, URLs and implementation details are not published.

---

## Write and Retrieval Behavior

Payload contracts help keep workflow behavior predictable.

For archive workflows, this depends on:

* stable identifiers
* required fields
* ordered messages
* existence-first checks
* controlled create/update behavior

For retrieval workflows, this depends on:

* explicit filters
* predictable response shapes
* clear distinction between validation errors and valid zero-result searches

This does not mean every internal platform behavior is controlled by the contract.

The contract defines the public boundary. Make and Notion still have their own platform constraints.

---

## Public vs Internal Contract

The public contract is not the full internal implementation model.

| Layer                            | Publicly documented? | Reason                      |
| -------------------------------- | -------------------: | --------------------------- |
| Public request/response boundary |                  Yes | Shows interface discipline  |
| JSON schemas                     |                  Yes | Shows validation discipline |
| Public-safe examples             |                  Yes | Shows practical behavior    |
| Internal Notion properties       |                   No | Implementation detail       |
| Make module mappings             |                   No | Tool-specific detail        |
| Private raw archive content      |                   No | Privacy and scope control   |
| Private IDs and URLs             |                   No | Security and privacy        |

---

## Architectural Role

The payload contract is the boundary between temporary AI/workflow output and persistent archive behavior.

ChatGPT, Claude, MCP-enabled workflows, webhooks or other clients can send structured input without owning the archive state.

The archive remains the source of record.
