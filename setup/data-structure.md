# Make Data Structure Reference

The public installer creates these four Make Data Structures automatically. Their definitions are versioned in [`../installer/manifest.json`](../installer/manifest.json), and the installer replaces the source-team IDs at every structural JSON-module binding before scenario creation.

Make Data Structures are target-team runtime resources. They are distinct from scenario public `io.input_spec`/`io.output_spec` definitions and from the JSON Schemas under [`../schemas/`](../schemas/). Updating one does not update the others.

## Provisioning order

1. `Weft - Archive Messages`
2. `Weft - Search Archive Response`
3. `Weft - Get Context Response`
4. `Weft - Daily Log Content`

On a fresh target, the installer creates each structure and captures its returned ID. On rerun, it reuses a recorded state ID after complete read-back. Without state, it reuses an existing structure only when the exact installer name and normalized schema match uniquely. A name collision, schema conflict, or duplicate match stops installation; the installer never guesses or deletes the conflicting resource.

## Weft - Archive Messages

- Purpose: serialize the normalized message array when the client does not supply `payload_json`.
- Kind: intermediate input shaping.
- Used by: `archive_conversation`, module 65 (`JSON > Create JSON`).
- Sample: [`Make/data-structures/archive-messages.sample.json`](./Make/data-structures/archive-messages.sample.json).

| Field | Make type | Required |
|---|---|---|
| `messages` | Array of collections | No at Data Structure level |
| `messages[].role` | Text | Yes |
| `messages[].content` | Text | Yes |

## Weft - Search Archive Response

- Purpose: shape and aggregate `search_archive` results.
- Kind: intermediate response shaping.
- Used by: modules 113, 117, 120, 123 and 126; aggregators 112, 116, 119, 122 and 125 target their `results` arrays.
- Sample: [`Make/data-structures/search-archive-response.sample.json`](./Make/data-structures/search-archive-response.sample.json).

The result collection contains `id`, `conversation_id`, `title`, `project`, `summary`, `key_insights`, and `model_origin`, all as text. The exported JSON-module metadata retains source labels `key-insights` and `model-origin`; the Data Structure and executable aggregator mappings use the proven underscore-form public properties.

## Weft - Get Context Response

- Purpose: shape full-content retrieval results before final aggregation.
- Kind: intermediate response shaping.
- Used by: modules 244, 246, 167, 238, 254, 256, 265 and 267.
- Sample: [`Make/data-structures/get-context-response.sample.json`](./Make/data-structures/get-context-response.sample.json).

The result collection contains text fields `conversation_id`, `title`, `project`, and `full_content`, plus number fields `message_count` and `content_length`.

## Weft - Daily Log Content

- Purpose: parse the structured JSON returned by the AI step in `create_daily_log` before the Daily Log record is updated.
- Kind: parser output contract.
- Used by: `create_daily_log`, module 45 (`JSON > Parse JSON`).
- Sample: [`Make/data-structures/daily-log-content.sample.json`](./Make/data-structures/daily-log-content.sample.json).

| Field | Make type | Required |
|---|---|---|
| `daily_summary` | Text | Yes |
| `actions` | Text | Yes |
| `title` | Text | Yes |

The canonical `create_daily_log` export explicitly selects the source Data Structure label `Daily Log Content`. The installer therefore treats this as a required fourth Data Structure, creates or uniquely reuses its target-team equivalent, and replaces the exported source binding during candidate generation.

## Public interfaces

The installer also verifies the public scenario interfaces independently of these structures. In particular, the `get_context` and `search_archive` result fields are guarded by `scripts/validate_examples.py` and by scenario read-back.

`Weft - Daily Log Content` is an internal parser contract for the optional supporting `create_daily_log` workflow. Its presence in the canonical blueprint is nevertheless structural: a candidate cannot be considered valid unless the source Data Structure binding is resolved to the target structure.
