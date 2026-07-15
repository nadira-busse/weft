# Public Contract Examples

This directory contains request and response examples for the documented Weft workflow boundaries.

The examples show the payload shapes used by the archive, search and get-context workflows.

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

Notion limits rich-text `text.content` values to 2000 characters.

The example response returns archived content with:

```text
Content length: 3673 characters
```

That is more than one Notion rich-text value can hold.

The system retrieves text from multiple stored blocks and returns it in the defined `get_context` response shape. The content comes from the stored archive blocks, not from short metadata fields or generated summaries.

Example content may be shortened for readability while preserving the response structure.
