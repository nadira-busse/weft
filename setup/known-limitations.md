# Known limitations

This document separates limitations in Weft itself from constraints imposed by the platforms it uses.

## Weft limitations

* `get_context` supports exact-date retrieval only when both `date_from` and `date_to` contain the same date. It does not support a date range; `search_archive` provides that search route instead.

* Repeating an accepted archive request with the same `conversation_id` reuses the existing Notion Archive record instead of creating another one. Existing page content is not overwritten: content from the new request is appended below it. Weft does not currently detect whether those appended blocks duplicate content that is already present.

* Weft does not support semantic search.

## Installer and recovery boundaries

* The installer does not automatically delete resources or perform a destructive rollback after a partial installation. Its state and reports should be kept so it can identify resources it created.

* If local installer state is lost after scenarios have already been created, a later preflight stops when it finds matching scenario names that it cannot identify as its own. The matching state file must be restored, or the collision must be reviewed manually.

## Platform constraints

Some setup steps still have to be completed in the Make or Notion interfaces because they depend on account-level resources or authorization that the installer cannot create or complete itself.

The optional `create_daily_log` workflow, for example, requires a Make `ai-provider` connection to exist before the installer can discover and bind it.

Make MCP can also reject an `archive_conversation` request before the scenario starts when the content contains a Markdown-formatted `python -m ...` command. The reproduced behavior and workaround are documented in the [Make MCP 403 troubleshooting note](../systems/archive-conversation/troubleshooting/make-mcp-403-markdown-python-module-command.md).

## Verification boundary

The installation uses a configurable `weft_timezone` value for archive datetime normalization and date-based searches. The supplied blueprints use `Europe/Amsterdam`, and that configuration has been runtime-tested. Other IANA timezone values can be configured, but equivalent runtime testing has not been performed for each timezone.
