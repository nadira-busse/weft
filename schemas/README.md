# Schemas

This directory contains the public JSON schemas for Weft payload boundaries.

Schemas define the minimum machine-checkable structure for public request and response contracts.

They are not a full publication of the internal Weft data model.

---

## Purpose

Schemas are included to show how Weft uses explicit contract validation at workflow boundaries.

They help ensure that:

* required fields are present
* field types are predictable
* workflow inputs and outputs remain structurally consistent
* public examples remain aligned with documented contracts
* implementation details stay separated from public contract boundaries

---

## Boundary Rule

The schemas describe public workflow boundaries only.

They intentionally do not expose:

* private Notion database structures
* Make module mappings
* internal relation-property names
* private IDs or URLs
* full raw archive payloads
* complete production storage records

---

## Archive Schemas

| Schema                                                                                                     | Purpose                                                   |
| ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [`archive/conversation-archive-request.schema.json`](./archive/conversation-archive-request.schema.json)   | Public request boundary for `archive_conversation`        |
| [`archive/conversation-archive-response.schema.json`](./archive/conversation-archive-response.schema.json) | Public response boundary for `archive_conversation`       |
| [`archive/message.schema.json`](./archive/message.schema.json)                                             | Public message item structure used by the archive request |

---

## Search Schemas

| Schema                                                                                       | Purpose                                     |
| -------------------------------------------------------------------------------------------- | ------------------------------------------- |
| [`search/search-archive-request.schema.json`](./search/search-archive-request.schema.json)   | Public input boundary for `search_archive`  |
| [`search/search-archive-response.schema.json`](./search/search-archive-response.schema.json) | Public output boundary for `search_archive` |

---

## Context Schemas

| Schema                                                                                   | Purpose                                  |
| ---------------------------------------------------------------------------------------- | ---------------------------------------- |
| [`context/get-context-request.schema.json`](./context/get-context-request.schema.json)   | Public input boundary for `get_context`  |
| [`context/get-context-response.schema.json`](./context/get-context-response.schema.json) | Public output boundary for `get_context` |

---

## Related

* [`../contracts/payload-contract.md`](../contracts/payload-contract.md)
* [`../examples/public-contracts/`](../examples/public-contracts/)
