# Case Study — Context Continuity System

## Overview

The Context Continuity System describes the retrieval side of Weft.

It exists because AI-assisted work often spans:

- multiple sessions
- multiple tools
- multiple models

Without external persistence, context becomes fragmented and has to be reconstructed manually.

Weft addresses this by storing selected context in a structured archive and retrieving it later through defined workflows.

---

## Problem

Large language models are stateless at the model level.

Built-in memory features can be useful, but they are not a controlled system of record. They may be limited, inconsistent or hard to inspect.

This leads to:

- repeated explanation of context
- fragmented reasoning
- disconnected decisions
- loss of traceability
- weak continuity between sessions

For multi-session work, context needs to live outside the chat itself.

---

## Objective

The objective is to make prior context retrievable for continued work.

The system supports:

- persisted archive records
- explicit search and retrieval workflows
- stable identifiers
- public payload boundaries
- controlled response shapes

The goal is not to make the AI client “remember everything”.

The goal is to make important context available again when the user needs to continue work.

---

## Scope

This case study covers the retrieval side of Weft.

Included:

- archive discovery
- archive search
- context retrieval
- response shaping
- explicit handling of lookup results

Excluded:

- archive write behavior
- semantic search
- automatic context synthesis
- multi-record context composition
- canonical knowledge promotion

Those excluded areas are documented as current limitations or future hardening opportunities.

---

## System Boundary

```text id="xbd0or"
AI Client
↓
Invocation Interface
↓
Orchestration Layer
↓
Context Layer
↓
Data Layer
````

The AI client can request context, but it does not own the archive state.

The workflow layer controls search and retrieval behavior.

The data layer stores the archive records and retrieved content.

---

## Retrieval Model

Context continuity is enabled through two operations.

### Discovery

Used when the correct archive record is not yet known.

```text id="xrluhk"
query → archive search → matching records
```

Discovery returns candidate records. It does not reconstruct the full context.

### Retrieval

Used when the target record or search boundary is known.

```text id="u1jz9h"
identifier or bounded query → context retrieval → ordered clean_text blocks
```

Retrieval returns stored archive content in a structured response shape.

---

## Retrieval Rules

The retrieval side follows these rules:

* retrieval should not modify stored records
* lookup outcomes must be handled explicitly
* zero, one and multiple results are different states
* public responses must not expose raw Notion internals
* retrieved text should follow the stored archive structure
* AI clients receive context, but do not become the source of truth

Any non-determinism belongs in the archived content or generated metadata, not in the retrieval boundary itself.

---

## Dependency on Archive System

Context continuity depends on prior archive operations.

```text id="9x4h1z"
interaction
→ archive
→ storage
→ search or retrieval
→ continued work
```

Without archive persistence, reliable retrieval is not possible.

---

## What This Enables

The retrieval side enables:

* finding earlier archive records
* retrieving stored context for continued work
* reducing repeated explanation across sessions
* keeping project decisions easier to trace
* supporting work across different AI clients

This is not full autonomous memory.

It is a controlled archive-and-retrieval layer that makes important context available outside the chat session.

---

## Current Boundary

Weft currently retrieves archived content through defined workflows.

It does not yet provide:

* semantic retrieval
* automatic cross-record synthesis
* autonomous memory management
* global context composition
* full knowledge promotion

That boundary matters. The current system is useful because it makes context retrievable, not because it solves every form of AI memory.

---

## Related

* [Archive Conversation System](../archive-conversation-system/)
* [Architecture Foundations](../../architecture/README.md)
* [Payload Contracts](../../contracts/payload-contract.md)
* [System Overview](../../architecture/system-overview.md)
* [Known Limitations](../../status/known-limitations.md)