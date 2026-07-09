# System in Production

This document explains which parts of Weft are actually running in my own workflow.

Weft is not only an architecture idea. It is based on a real Make + Notion system that I use for AI-assisted project work.

The public repository does not contain the full private implementation. It documents the architecture, contracts, examples, proof cases and screenshots that show how the system works.

---

## What Is Running

The current system includes:

* **archive_conversation** — stores selected AI interactions and workflow outputs as structured records in Notion
* **search_archive** — searches archive records by conversation ID, project, date range or query
* **get_context** — retrieves archived content so earlier work can be reused later
* **notion_text_formatter** — extracts text from Notion block structures
* **Daily Log aggregation** — groups archive records per working day
* **Project aggregation** — links archive records back to project records
* **Error logging** — captures workflow execution errors separately from archive records

The system currently runs through Make, Notion and MCP-enabled workflow invocation.

---

## Notion Database Structure

The running implementation uses several Notion databases.

The full private database setup is not published, but the public architecture is based on these components:

| Component              | Role                                                               |
| ---------------------- | ------------------------------------------------------------------ |
| **Archive database**   | Source of record for archived AI interactions and workflow outputs |
| **Project database**   | Groups archive records by project                                  |
| **Daily log database** | Groups archive records by working day                              |
| **Error log database** | Captures runtime errors and execution observations                 |

Archive records include stable identity, timing metadata, source/model metadata, content body, derived metadata, project relations, daily-log relations and execution snapshots.

The private Notion schema is intentionally not published because it contains implementation details and personal workflow structure.

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

Workflow errors are captured separately from normal archive records. This matters because an execution error is not automatically the same as a product bug.

---

## Cross-Model Context Transfer

Weft supports context transfer between Claude and ChatGPT through the same archive layer.

Both clients can work with the same stored context because the archive sits outside the AI client.

In practice, this means I can archive work from one AI client, retrieve it later and continue the project in another AI client without rebuilding the same context manually.

This is one of the reasons I built Weft: important project state should not depend on one chat, one model or one interface.

---

## Make Scenario Architecture

The running system uses multiple Make scenarios:

* **archive_conversation** — main write path for storing selected conversations and workflow outputs
* **search_archive** — search path for finding archive records
* **get_context** — retrieval path for rebuilding usable context from stored records
* **notion_text_formatter** — supporting subscenario for Notion block text extraction
* **daily_log aggregation** — separate workflow for grouping archive entries per working day

The scenarios follow the same basic design approach:

* validate the incoming request shape
* check whether related records already exist
* route based on explicit conditions
* write or update records through stable identifiers
* keep workflow errors separate from archive records
* return a structured response to the caller

Make and Notion do not provide hard transactional guarantees.

The goal is workflow-level reliability within those constraints: clear payloads, stable identifiers, explicit routing and traceable failures.

---

## Public Artifacts

The public repository shows the architecture and evidence, not the full private runtime.

Published:

* workflow descriptions
* request and response contracts
* JSON schemas for payload boundaries
* example payloads
* reusable workflow patterns
* runtime proof cases
* screenshots with sensitive details omitted
* known limitations

Not published:

* full Make scenario blueprints
* private Notion database schemas
* internal Notion IDs
* webhook URLs
* API keys or credentials
* private archive content
* full MCP configuration


