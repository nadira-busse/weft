# Archive-First Context Flow

This document describes the public architecture behind archiving AI-assisted work in Weft and retrieving it later as runtime context.

It explains the workflow boundary, not a deployable Make blueprint.

Implementation-specific orchestration logic, Make module configuration, private mappings, filters, runtime payloads and database relation details are intentionally omitted.

Public schemas and contract examples are documented elsewhere in the repository to show the workflow boundaries without exposing live workflow data.

![Archive-First Context Flow](../diagrams/archive-conversation-flow.svg)

---

## Two Phases, Not One Pipeline

This flow has two separate phases that happen at different times.

It is not one continuous pipeline.

### 1. Archive

A client or scheduled workflow invocation sends a structured payload through the invocation interface.

The orchestration layer validates the payload before linking. If a required field — such as project — is missing from the payload, the record is marked invalid, archiving stops before any lookup occurs, and the missing fields are returned to the caller.

For valid payloads, the archive record is normalized, linked and stored:

- Project records — matched by name; if no matching project exists, a new project record and project key are created automatically.
- Daily log records — matched by date; if no daily log exists for that day, one is created automatically on first archival.

The archive record becomes the persistent source record for the archived interaction.

### 2. Retrieve

Later, in a separate session and only through an explicit request, the system can retrieve archived content.

Retrieval can happen through:

* direct identifier lookup
* search followed by selection
* context reconstruction from a stored archive record

The retrieved content is rebuilt from the archived record.

Retrieval does not reinterpret meaning, generate missing source content or modify the stored archive record.

---

## Layer Responsibilities

This flow follows the same layer model described in:

* [`layer-model.md`](./layer-model.md)
* [`system-overview.md`](./system-overview.md)

| Layer                | Responsibility in this flow                                                         |
| -------------------- | ----------------------------------------------------------------------------------- |
| AI / Client Layer    | Provides the interaction or workflow output that may be archived                    |
| Invocation Interface | Defines the request boundary into the orchestration system                          |
| Orchestration Layer  | Handles validation, routing, linking, writes, retries and failure handling          |
| Context Layer        | Shapes archive payloads and reconstructs stored records into usable runtime context |
| Data Layer           | Stores archive records, relations and operational evidence                          |

The AI client does not own persistence.

The archive is the source of record for explicitly archived workflow state.

---

## Validation, Monitoring and Error Handling

Validation, monitoring and error handling are cross-cutting concerns.

They are not one single sequential step in the flow.

In the current implementation, the orchestration layer is implemented in Make. It defines how Weft validates inputs, routes execution, handles failures and surfaces operational outcomes.

Some transient execution failures may be handled through Make platform configuration, such as retry settings, timeouts or error handlers.

Persistent failures are surfaced through controlled failure handling and operational logging.

---

## Design Rationale

The archive flow exists because AI chat history is not a reliable source of project memory.

Weft stores selected AI-assisted work as structured, searchable and project-linked archive records.

Runtime context is reconstructed from archived evidence only when requested.

This keeps a clear distinction between:

* what is stored
* what is retrieved
* what is currently in use

The result is a system where project context can move across sessions, AI clients and workflow tools without depending on one temporary chat.
