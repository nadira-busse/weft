# Schemas

This directory contains JSON Schemas for the documented Weft request and response boundaries.

The schemas define the minimum machine-checkable structure for each contract and are used to verify required fields, field types and alignment with the public examples.

---

## Available Schemas

| Workflow | Schema | Purpose |
| --- | --- | --- |
| Archive Conversation | [`archive/conversation-archive-request.schema.json`](./archive/conversation-archive-request.schema.json) | Request boundary for `archive_conversation` |
| Archive Conversation | [`archive/conversation-archive-response.schema.json`](./archive/conversation-archive-response.schema.json) | Response boundary for `archive_conversation` |
| Archive Conversation | [`archive/message.schema.json`](./archive/message.schema.json) | Message item used by the archive request |
| Search Archive | [`search/search-archive-request.schema.json`](./search/search-archive-request.schema.json) | Request boundary for `search_archive` |
| Search Archive | [`search/search-archive-response.schema.json`](./search/search-archive-response.schema.json) | Response boundary for `search_archive` |
| Get Context | [`context/get-context-request.schema.json`](./context/get-context-request.schema.json) | Request boundary for `get_context` |
| Get Context | [`context/get-context-response.schema.json`](./context/get-context-response.schema.json) | Response boundary for `get_context` |

---

## Related

* [`../contracts/payload-contract.md`](../contracts/payload-contract.md)
* [`../examples/public-contracts/`](../examples/public-contracts/)
