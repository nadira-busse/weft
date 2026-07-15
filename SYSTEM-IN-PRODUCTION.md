# System in Production

This document explains how Weft runs in my own workflow.

Weft is based on a real Make + Notion system that I use for AI-assisted project work.

---

## What Is Running

The system currently runs through Make, Notion and MCP-enabled workflow invocation.

### Notion

The running implementation uses these databases:

| Component              | Role                                                               |
| ---------------------- | ------------------------------------------------------------------ |
| **Archive database**   | System of record for archived AI interactions and workflow outputs |
| **Project database**   | Groups archive records by project                                  |
| **Daily log database** | Groups archive records by working day                              |
| **Error log database** | Captures runtime errors and execution observations                 |

Archive records include stable identity, timing metadata, source/model metadata, content body, derived metadata, project relations, daily-log relations and execution snapshots.

### Make

The running system includes these scenarios and workflow components:

* **archive_conversation** — stores selected AI interactions and workflow outputs as structured records
* **search_archive** — searches archive records by conversation ID, project, date range or query
* **get_context** — retrieves archived content for later use
* **notion_text_formatter** — extracts text from Notion block structures
* **Daily Log aggregation** — groups archive records per working day
* **Project aggregation** — links archive records back to project records
* **Error logging** — captures workflow execution errors separately from archive records

The scenarios follow the same basic design approach:

* validate the incoming request shape
* check whether related records already exist
* route based on explicit conditions
* write or update records through stable identifiers
* keep workflow errors separate from archive records
* return a structured response to the caller

Make and Notion do not provide hard transactional guarantees.

Weft therefore relies on explicit workflow checks and recoverable execution paths rather than platform-level transactions.

---

## Runtime Evidence

The running system contains real work sessions from projects including Weft, Kelvior Agent Decision Gate and other AI-assisted work.

The evidence is visible through:

* archive records with stored project context
* project records with relation-based rollups
* daily logs grouped from archive entries
* error logs for Make, MCP and webhook execution issues
* screenshots included in the public repository
* proof cases based on issues found during implementation

Workflow errors are captured separately from normal archive records. An execution error is not automatically the same as a product bug.

---

## Cross-Model Context Transfer

Weft supports context transfer between Claude and ChatGPT through the same archive layer.

Both clients can work with the same stored context because the archive sits outside the AI client.

In practice, I can archive work from one AI client, retrieve it later and continue the project in another AI client without rebuilding the same context manually.

Important project state therefore does not depend on one chat, one model or one interface.

See a recorded example of this flow: [Cross-model context transfer demo](your-link-here)