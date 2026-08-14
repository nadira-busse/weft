# Public Payload Contracts

The exported Make `io.input_spec` and `io.output_spec` definitions are the implementation source for these three MCP contracts. JSON Schemas are canonical machine-readable projections under [`../schemas/`](../schemas/); sanitized valid and invalid fixtures are under [`../examples/public-contracts/`](../examples/public-contracts/).

## `archive_conversation`

Required request fields are `conversation_id`, `conversation_title`, `project`, `extraction_type`, `start_time`, `message_count` and a non-empty `messages` array. Each message contains `role` and `content` text. Optional enrichment fields are `end_time`, `summary`, `action_items`, `key_insights`, `categories`, `source`, `source_platform`, `payload_json`, `status`, `priority` and `sentiment`.

`start_time` and `end_time` accept an ISO datetime or local `HH:mm` value. The exported workflow uses `Europe/Amsterdam` when normalizing local values.

`conversation_id` is trimmed at the deterministic normalization boundary. A value containing only whitespace is invalid and returns `validation_error` before any Notion lookup or write. Successful and blocked responses return that same canonical, trimmed identity.

Archive writes use the normalized title, timestamps, message count, project key, source, platform, extraction type, sentiment, priority, action items, key insights, categories, status and storage payload. Summary remains the supplied summary because the workflow has no separate canonical summary variable. Categories and status retain their exported array handling.

The response exposes `status`, `conversation_id`, `record_id`, `notion_url`, `error_type`, `message`, `module` and `timestamp`. Only `status` and `conversation_id` are required by the public output specification; route-specific fields are optional. Runtime routes use `success`, `partial`, `blocked` and `error` status values.

A conversation ID is canonically bound to one project. When an existing Archive stores a different canonical project key, the request returns `status: blocked`, `error_type: PROJECT_CONFLICT`, the existing Archive `record_id` and `notion_url`, and the exact message `Conversation exists under a different project; request blocked without changes.` The conflict route does not create or recreate a Project, update Archive properties, append page content, create a duplicate Archive, or create an Error Log.

When a requested Project is absent, the workflow searches Archive before creating the Project. A matching existing Archive with no valid Project relation takes the repair route: it recreates the Project once, updates the existing Archive relation, appends the new content, and returns the original Archive identity. A conflicting existing Archive takes the no-write blocked route instead.

Schemas: [`request`](../schemas/archive-conversation/request.schema.json), [`response`](../schemas/archive-conversation/response.schema.json).

## `search_archive`

The request accepts `query`, `conversation_id`, `project`, `date_from`, `date_to` and `limit`. At least one route driver is required. Date searches supply both date fields. The exported default limit is 10 and validation rejects non-positive values.

The five established routes are evaluated for conversation ID, exact date, date range, normalized project and query. Query searches Title, Summary, Full content and Key insights. Date-range upper bounds are calculated in `Europe/Amsterdam`.

The response uses the top-level field `results_count` exactly as exported. Each result contains:

```json
{
  "id": "...",
  "conversation_id": "...",
  "title": "...",
  "project": "...",
  "summary": "...",
  "key_insights": "...",
  "model_origin": "..."
}
```

Successful and empty lookups return `success: true`; validation envelopes return `success: false`. Both retain `results`, `results_count`, `meta` and `message`.

Schemas: [`request`](../schemas/search-archive/request.schema.json), [`response`](../schemas/search-archive/response.schema.json).

## `get_context`

The request accepts `query`, `conversation_id`, `project`, `date_from`, `date_to` and `limit`. It supports four established retrieval modes: query, conversation ID, exact date and normalized project.

Exact-date retrieval requires both `date_from` and `date_to`, and the values must be equal. JSON Schema can require the pair but cannot compare their values; the local validator therefore applies an additional semantic equality check. The exported executable flow defaults the limit to 5 and rejects non-positive values. Although its input help mentions a maximum of 20, the flow does not enforce that maximum, so the public schema does not claim one.

Each result contains:

```json
{
  "title": "...",
  "project": "...",
  "full_content": "...",
  "message_count": 0,
  "content_length": 0,
  "conversation_id": "..."
}
```

The response uses `result_count` (singular), a structured `results` array, `meta`, and a route-specific `message`. Successful routes set `meta.retrieval_mode` to `query`, `conversation_id`, `date` or `project`. Empty results remain successful; invalid input returns `success: false`.

Schemas: [`request`](../schemas/get-context/request.schema.json), [`response`](../schemas/get-context/response.schema.json).

## Validation

Run `python scripts/validate_examples.py` from the repository root. It checks all six schemas, every registered public fixture, all seven current Archive V4 regression suites and their JSON fixtures, expected invalid fixtures, exact-date equality, and the two exported output-spec result structures. The canonical regression evidence is the [V4 regression report](../regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md).
