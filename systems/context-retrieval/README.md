# Context Retrieval

Context Retrieval is Weft's read path. `search_archive` finds matching Archive records, while `get_context` returns the stored conversation content of matching Archive records.

The two operations use the same Archive data for different purposes. Search returns compact results that help a caller choose a record. Context retrieval returns the stored conversation content needed to continue earlier work.

One failure showed why a successful Make run was not enough. `search_archive` found several matching Notion records, but the response returned only one because the resulting bundles had not been combined into the final results array. The scenario completed successfully, while the returned result was still wrong.

Three Make workflows implement this read path:

* [`search_archive` in Make](https://eu1.make.com/public/shared-scenario/kMLUtxQJb2L/weft-search-archive)
* [`get_context` in Make](https://eu1.make.com/public/shared-scenario/vH1RABSc2t1/weft-get-context)
* [`notion_text_formatter` in Make](https://eu1.make.com/public/shared-scenario/CxwoCdhvFcx/weft-notion-text-formatter)

Their exported blueprints are:

* [`weft_search_archive.json`](../../setup/Make/blueprints/weft_search_archive.json)
* [`weft_get_context.json`](../../setup/Make/blueprints/weft_get_context.json)
* [`weft_notion_text_formatter.json`](../../setup/Make/blueprints/weft_notion_text_formatter.json)

## When a successful search returned the wrong object

Make search modules emit bundles. Several matching bundles are not automatically combined into one `results` array, and Return Output does not perform that aggregation.

Two related failures appeared while the search routes were being stabilized.

One path had no final aggregation, so several valid matches produced only one returned result. Another projection was bound to an older or incompatible aggregator structure, which produced incomplete fields and exposed raw Notion data instead of the expected response fields.

In both cases the Notion lookup was correct and the response was wrong.

The corrected path is explicit:

```text
Notion search

→ map each record to the fields returned by `search_archive`

→ aggregate all mapped records into one array

→ return one response
```

Search returns the fields defined in the [payload contract](../../contracts/payload-contract.md), including `conversation_id`, `key_insights` and `model_origin`, rather than raw `properties_value` data.

The multi-result regression checks both `results_count` and the number of objects in `results`. JSON Schema can validate their types and shapes, but not that both counts are equal, so that equality is checked separately.

## Typed Notion values had to stay typed

Other successful routes returned `null` even though Notion contained the value.

The fixes followed the value shape returned by Notion instead of changing the response field:

* `conversation_id` is stored as rich text and is read from its `plain_text` projection.
* `message_count` comes from a Notion Number property and remains a JSON number rather than being converted to text.
* A Notion relation is an array of objects. The full `relation_field[]` enters the Iterator; inside it, the page ID is the current relation object's `N.value.id`, not the complete `N.value` object.

The relation distinction fixed two observed failures: passing an object where Notion expected a UUID, and processing only one item from a relation that contained more than one entry.

## Date routes

`search_archive` treats equal `date_from` and `date_to` values as an exact-date search.

When `date_from` is earlier than `date_to`, the workflow searches the inclusive date range between them. The lower and upper bounds use AND semantics: the stored start time must be on or after `date_from` and on or before the end of `date_to`.

The upper boundary is calculated using the installation's `weft_timezone` setting. The supplied blueprint uses `Europe/Amsterdam`.

A `date_from` later than `date_to` is invalid. Date searches also require both fields.

`get_context` does not support a date range. Its date route retrieves by exact date only, so `date_from` and `date_to` must both be present and contain the same date.

This difference is deliberate: `search_archive` supports date ranges, while `get_context` retrieves by exact date only.

## Full content had to be selected before formatting

The archived Notion page uses an established nine-item layout.

`get_context` originally sent that complete page layout to `notion_text_formatter`. As a result, `full_content` included labels and metadata such as `Conversation ID` and `Message count` instead of only the archived conversation.

The formatter was processing the content it received correctly. Changing the shared formatter to understand one parent's page layout would have moved the defect instead of fixing it.

The correction stayed in `get_context`.

`get_context` now selects only the stored conversation block before sending it to `notion_text_formatter`. In the current blueprint this is done with `slice(...; 2; 3)`. Metadata remains in separate response fields, and `content_length` measures the returned conversation content.

The slice is an implementation detail rather than part of the payload contract.

In the tested fixture, 10,000 characters of stored content returned as 10,011 characters including the expected `ASSISTANT: ` prefix. The test verified the beginning, end and internal checkpoints, found no truncation or duplication, excluded the page labels and confirmed that `content_length` matched the returned text.

This verifies the current page layout and that fixture. It does not establish behavior for every possible content size or a different Notion page layout.

## Evidence and limits

The [Search Archive run-history screenshot](./assets/screenshots/make-search-archive-run-history.png) and [Get Context run-history screenshot](./assets/screenshots/make-get-context-run-history.png) show successful workflow runs. Route-specific behavior is covered by the contract fixtures and regression checks rather than by the screenshots alone.

`search_archive` and `get_context` use explicit criteria supplied by the caller. Weft does not support semantic search.

Date-based searches use the installation's `weft_timezone` setting. The supplied configuration uses `Europe/Amsterdam`, which is the timezone covered by the current runtime evidence.

`get_context` currently relies on the existing Notion page layout when selecting the stored conversation block. If that layout changes, the content-selection step must be updated.
