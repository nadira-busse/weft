# Public Contract Examples

This directory contains public-safe request and response examples for the Weft workflow boundaries.

The examples show the external payload shapes used by the public documentation. They do not expose private Notion IDs, internal URLs, full database structures, Make module mappings or sensitive runtime data.

---

## Included Examples

| Folder                                 | Purpose                                                                            |
| -------------------------------------- | ---------------------------------------------------------------------------------- |
| [`archive-conversation/`](./archive-conversation/)               | Example request and response for archiving an AI interaction or workflow output    |
| [`search-archive/`](./search-archive/) | Example request and response for finding archived records through explicit filters |
| [`get-context/`](./get-context/)       | Example request and response for retrieving archived content as reusable context   |

---

## Important Note on `get_context`

The `get-context` response reflects block-based retrieval from the archive context layer.

Notion limits each text block to 2000 characters. The example response reconstructs a record with:

```text
Content length: 3673 characters
```

That is more than one block's worth of content.

The system aggregates across multiple stored blocks and returns the retrieved content as a continuous response field. It is not reconstructed from short metadata fields or generated summaries.

Long public example content may be shortened in this repository for readability, while preserving the actual public response shape.

---

## Boundary

These examples represent public workflow contracts.

They are not complete private runtime payloads and they are not deployable Make scenario exports.
