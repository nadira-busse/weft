# Payload contracts

The three MCP operations use fixed request and response structures. Those structures are defined in the exported Make scenarios and mirrored in JSON Schemas so they can be checked without running the workflows.

The schemas are grouped by operation:

* [`archive_conversation`](../schemas/archive-conversation/)
* [`search_archive`](../schemas/search-archive/)
* [`get_context`](../schemas/get-context/)

Sanitized example payloads are stored under [`examples/contracts/`](../examples/contracts/). Files ending in `.invalid.json` are intentionally invalid and are expected to fail when [`scripts/validate_examples.py`](../scripts/validate_examples.py) runs.

Some behavior cannot be expressed by JSON Schema alone. The validator and regression tests therefore also check rules that depend on values or stored state, such as equal dates for exact-date `get_context` requests and project conflicts during archiving.

## `archive_conversation`

### Request

The `archive_conversation` request requires:

* `conversation_id`
* `conversation_title`
* `project`
* `extraction_type`
* `start_time`
* `message_count`
* a non-empty `messages` array

Each message contains a `role` and `content`.

The request can also include:

* `end_time`
* `summary`
* `action_items`
* `key_insights`
* `categories`
* `source`
* `source_platform`
* `payload_json`
* `status`
* `priority`
* `sentiment`

### Datetimes

`start_time` and `end_time` accept either an ISO 8601 datetime or a local `HH:mm` value.

Local values are interpreted using the installation's `weft_timezone` setting. The supplied `archive_conversation` blueprint sets this to `Europe/Amsterdam`.

The workflow normalizes these values before validating or storing them. This was added because an earlier implementation accepted `HH:mm` at the input boundary but then validated the original value as though it already had to be an ISO datetime.

A supplied `end_time` is preserved and normalized. When `end_time` is omitted, the workflow uses the current archive time.

A local `HH:mm` value does not contain a calendar date. If a conversation is archived on a later day, the original date cannot be reconstructed from that value alone. In that case, the request should provide at least a dated `start_time`.

The `Europe/Amsterdam` configuration has been runtime-tested. The repository does not contain equivalent runtime evidence for every other IANA timezone.

### Conversation identity

`conversation_id` is trimmed during normalization.

A value containing only whitespace is invalid. The workflow returns a `validation_error` before performing a Notion lookup or write.

The fixtures include this case explicitly:

[`whitespace-conversation-id.invalid.json`](../examples/contracts/archive-conversation/whitespace-conversation-id.invalid.json)

Successful and blocked responses return the same trimmed conversation ID used by the workflow internally.

### Stored values

Before writing to Notion, the workflow normalizes the values used for the Archive record, including:

* title
* timestamps
* message count
* project key
* source and source platform
* extraction type
* sentiment
* priority
* action items
* key insights
* categories
* status
* storage payload

`summary` remains the summary supplied by the caller. The workflow does not create a separate normalized summary value.

Categories and status retain the array handling used by the exported workflow.

### Response

The response can contain:

* `status`
* `conversation_id`
* `record_id`
* `notion_url`
* `error_type`
* `message`
* `module`
* `timestamp`

Only `status` and `conversation_id` are required for every response. Other fields depend on the route that was taken.

The current workflow returns these status values:

* `success`
* `partial`
* `blocked`
* `error`

### Existing conversations and project conflicts

A `conversation_id` belongs to one normalized project identity.

If the Archive already exists under a different project key, Weft returns:

```text
status: blocked
error_type: PROJECT_CONFLICT
```

The response also contains the existing Archive `record_id` and `notion_url`, together with:

```text
Conversation exists under a different project; request blocked without changes.
```

That route does not:

* create or recreate a Project;
* update the Archive;
* append page content;
* create another Archive;
* create an Error Log.

The fixtures include a project-conflict response so this no-change route can be checked against the expected payload:

[`project-conflict.response.json`](../examples/contracts/archive-conversation/project-conflict.response.json)

A missing Project record is handled differently.

If the Archive already contains the same project key but its Project relation is missing or invalid, the workflow recreates the Project once, reconnects the existing Archive, appends the new content, and returns the original Archive identity.

It does not create another Archive merely because the related Project record disappeared.

Request schema: [`request.schema.json`](../schemas/archive-conversation/request.schema.json)

Response schema: [`response.schema.json`](../schemas/archive-conversation/response.schema.json)

Examples: [`archive_conversation`](../examples/contracts/archive-conversation/)

## `search_archive`

### Request

The `search_archive` request supports these fields:

* `query`
* `conversation_id`
* `project`
* `date_from`
* `date_to`
* `limit`

At least one supported search criterion is required.

Date searches require both `date_from` and `date_to`.

The default limit in the exported workflow is `10`. Values of `0` or lower are rejected.

### Search routes

The workflow supports five search routes:

* conversation ID;
* exact date;
* date range;
* normalized project;
* text query.

The route is selected from the criteria supplied in the request.

A conversation ID search uses `conversation_id`.

A project search uses the normalized project key.

A text query searches the stored Title, Summary, Full content, and Key insights fields.

### Date searches

When `date_from` and `date_to` are equal, the workflow performs an exact-date search.

When `date_from` is earlier than `date_to`, the workflow searches the inclusive date range between them.

A `date_from` later than `date_to` is invalid.

The workflow uses `weft_timezone` when converting the requested date boundary into the timestamp used for the Notion search. The supplied blueprint sets this value to `Europe/Amsterdam`.

### Response

The top-level result count is named:

```text
results_count
```

Each result contains:

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

A valid search returns `success: true`, including when no records match.

Validation failures return `success: false`.

The response contains:

* `results`
* `results_count`
* `meta`
* `message`

Request schema: [`request.schema.json`](../schemas/search-archive/request.schema.json)

Response schema: [`response.schema.json`](../schemas/search-archive/response.schema.json)

Examples: [`search_archive`](../examples/contracts/search-archive/)

## `get_context`

### Request

The `get_context` request supports these fields:

* `query`
* `conversation_id`
* `project`
* `date_from`
* `date_to`
* `limit`

The current workflow supports four retrieval modes:

* text query;
* conversation ID;
* exact date;
* normalized project.

Unlike `search_archive`, `get_context` does not support a date range.

For date retrieval, both `date_from` and `date_to` must be present and must contain the same date.

JSON Schema can require both fields, but it cannot express that their values must be equal. [`scripts/validate_examples.py`](../scripts/validate_examples.py) therefore performs that additional check.

The exported workflow defaults `limit` to `5` and rejects values of `0` or lower.

### Response

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

The top-level count is named:

```text
result_count
```

This differs from the `results_count` field used by `search_archive` because that is how the exported workflows currently return their responses.

Successful retrieval sets `meta.retrieval_mode` to one of:

* `query`
* `conversation_id`
* `date`
* `project`

No matches still produce a successful response.

Invalid input returns `success: false`.

Request schema: [`request.schema.json`](../schemas/get-context/request.schema.json)

Response schema: [`response.schema.json`](../schemas/get-context/response.schema.json)

Examples: [`get_context`](../examples/contracts/get-context/)

## Validation

From the repository root, run:

```powershell
python scripts/validate_examples.py
```

The script currently checks:

* all six request and response schemas;
* the registered example payloads;
* fixtures that are expected to fail validation;
* the seven Archive V4 regression suites and their JSON fixtures;
* the extra equality rule for exact-date `get_context` requests;
* the exported result structures for `search_archive` and `get_context`.

The Archive regression results are recorded in the [V4 regression report](../regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md).

These checks validate the stored schemas, fixtures, and recorded regression expectations. They do not replace runtime verification after a Make blueprint or workflow behavior changes.
