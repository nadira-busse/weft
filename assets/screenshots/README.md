# Screenshots

This folder contains public-safe screenshots used as runtime evidence for Weft.

The screenshots show that key workflows run in practice. They do not expose private Make scenario logic, module mappings, webhook URLs, Notion database IDs, internal relations or raw archive content.

---

## Included screenshots

### MCP Server Connected

![ChatGPT MCP server connected](chatgpt-mcp-server-connected.png)

![Claude MCP server connected](claude-mcp-server-connected.png)

These screenshots show the same private `Make_MCP_Server` connection available in both ChatGPT and Claude.

Together, they provide evidence that Weft can be invoked through an MCP-enabled boundary from multiple AI clients, rather than being tied to one chat interface.

Runtime workflow execution is documented separately through the Make and Notion evidence screenshots below.

### Make — Archive Conversation

![Archive workflow run history](make-archive-conversation-run-history.png)

Shows repeated successful executions of the `archive_conversation` scenario and provides operational evidence that archive writes run in practice.

### Make — Search Archive

![Search archive run history](make-search-archive-run-history.png)

Shows runtime evidence that the `search_archive` workflow executes successfully against the archive database.

### Make — Get Context

![Get context run history](make-get-context-run-history.png)

Shows runtime evidence that archived context can be retrieved through the `get_context` workflow.

### Notion — Archive Database

![Notion archive database](notion-archive-db-evidence-view.png)

Shows structured archive records with stable conversation identifiers, project linkage, source metadata, extraction type, model origin and archive status.

### Notion — Error Logs

![Notion error logs](notion-error-logs.png)

Shows that workflow errors are logged for observability and debugging.

---

## Boundary

These screenshots support that Weft is a working system in my own workflow.

They do not claim that Weft is a finished product, a SaaS platform or a generally deployable system.
