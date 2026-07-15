# Archive-First Context Flow

This document explains how Weft archives AI-assisted work and retrieves it later as runtime context.

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

- direct lookup by conversation ID
- search by project, date range or query, followed by record selection

After a record is selected, `get_context` retrieves the stored content and returns it in a structured response.

Retrieval does not reinterpret meaning, generate missing source content or modify the stored archive record.

---

## Layer Responsibilities

This flow follows the same layer model described in:

- [`layer-model.md`](./layer-model.md)
- [`system-overview.md`](./system-overview.md)

| Layer                | Responsibility in this flow                                                    |
| -------------------- | ------------------------------------------------------------------------------ |
| AI / Client Layer    | Provides the interaction or workflow output that may be archived               |
| Invocation Interface | Defines the request boundary into the orchestration system                     |
| Orchestration Layer  | Handles validation, routing, linking, writes, retries and failure handling     |
| Context Layer        | Shapes archive payloads and retrieves stored records as usable runtime context |
| Data Layer           | Stores archive records, relations and operational evidence                     |

The AI client does not own persistence.

The archive is the system of record for explicitly archived workflow state.

---

## Validation, Monitoring and Error Handling

Validation, monitoring and error handling are cross-cutting concerns.

They are not one single sequential step in the flow.

In the current implementation, the orchestration layer is implemented in Make. It defines how Weft validates inputs, routes execution, handles failures and surfaces operational outcomes.

Some transient execution failures may be handled through Make platform configuration, such as retry settings, timeouts or error handlers.

Persistent failures are surfaced through controlled failure handling and operational logging.
