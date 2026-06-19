# Screenshots

This folder contains public-safe screenshots used as runtime evidence for Weft.

The screenshots show that key workflows run in practice. They do not expose private Make scenario logic, module mappings, webhook URLs, Notion database IDs, internal relations or raw archive content.

---

## Included screenshots

### Make — Archive Conversation

![Archive workflow run history](make-archive-conversation-run-history.png)

Shows repeated successful executions of the `archive_conversation` scenario. This provides operational evidence that archive writes run in practice, while detailed scenario logic, mappings, module configuration and runtime payload instances remain intentionally unpublished.

### Make — Search Archive

![Search archive run history](make-search-archive-run-history.png)

Shows runtime evidence that the `search_archive` workflow executes successfully. Detailed query construction, Notion filter configuration and internal mapping logic are intentionally unpublished.

### Make — Get Context

![Get context run history](make-get-context-run-history.png)

Shows runtime evidence that archived context can be retrieved through the `get_context` workflow. Internal block reconstruction, mapping details and private archive content are intentionally unpublished.

### Notion — Archive Database

![Notion archive database](notion-archive-db-evidence-view.png)

Shows structured archive records with stable conversation identifiers, project linkage, source metadata, extraction type, model origin and archive status. Raw content, payload JSON, detailed relations and private workflow data are intentionally hidden.

### Notion — Error Logs

![Notion error logs](notion-error-logs.png)

Shows that workflow errors are logged for observability and debugging. Private error payloads, internal identifiers and detailed scenario mappings are intentionally hidden.

---

## Boundary

These screenshots support the claim that Weft is a working system in the author’s own workflow.

They do not claim that Weft is a finished product, a SaaS platform or a generally deployable system.
