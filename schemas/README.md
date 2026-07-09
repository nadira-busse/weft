# Schemas

This directory contains JSON schemas for the documented Weft payload boundaries.

Schemas define the minimum machine-checkable structure for request and response contracts.

---

## Purpose

Schemas are included to show how Weft uses explicit contract validation at workflow boundaries.

They help ensure that:

* required fields are present
* field types are predictable
* workflow inputs and outputs remain structurally consistent
* examples remain aligned with documented contracts
* contract validation stays separate from implementation details

---

## Boundary Rule

The schemas describe workflow contract boundaries only.

They do not describe the full internal data model, Make scenario mappings or Notion database structure.

---

## Archive Schemas

| Schema                                                                                                     | Purpose                                                   |
| ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [`archive/conversation-archive-request.schema.json`](./archive/conversation-archive-request.schema.json)   | Request boundary for `archive_conversation`        |
| [`archive/conversation-archive-response.schema.json`](./archive/conversation-archive-response.schema.json) | Response boundary for `archive_conversation`       |
| [`archive/message.schema.json`](./archive/message.schema.json)                                             | Message item structure used by the archive request |

---

## Search Schemas

| Schema                                                                                       | Purpose                                     |
| -------------------------------------------------------------------------------------------- | ------------------------------------------- |
| [`search/search-archive-request.schema.json`](./search/search-archive-request.schema.json)   | Input boundary for `search_archive`  |
| [`search/search-archive-response.schema.json`](./search/search-archive-response.schema.json) | Output boundary for `search_archive` |

---

## Context Schemas

| Schema                                                                                   | Purpose                                  |
| ---------------------------------------------------------------------------------------- | ---------------------------------------- |
| [`context/get-context-request.schema.json`](./context/get-context-request.schema.json)   | Public input boundary for `get_context`  |
| [`context/get-context-response.schema.json`](./context/get-context-response.schema.json) | Output boundary for `get_context` |

---

## Related

* [`../contracts/payload-contract.md`](../contracts/payload-contract.md)
* [`../examples/public-contracts/`](../examples/public-contracts/)
