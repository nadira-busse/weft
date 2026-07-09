# Case Study — Context Continuity System

## Overview

The Context Continuity System describes the retrieval side of Weft.

It exists because AI-assisted work often continues across sessions, AI clients and workflow tools.

Without external persistence, context becomes fragmented and has to be reconstructed manually.

Weft addresses this by storing selected context in a structured archive and retrieving it later through defined workflows.

---

## Problem

Modern AI clients increasingly include memory and chat-history features.

Those features can be useful, but they do not always return the exact context needed for continued project work. They can miss relevant details, surface the wrong prior context, or make it difficult to inspect why a specific memory was used.

For multi-session work, this can still lead to:

- repeating context that was already discussed
- reconnecting decisions manually
- searching through earlier conversations
- uncertainty about which version of the context is current
- weaker continuity between sessions, tools or AI clients

Weft addresses this by keeping selected context in a structured archive that can be searched and retrieved explicitly.

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

This case study covers the retrieval side of Weft: finding archived records and returning stored context in a structured response so work can continue in an AI client.

The archive write path is covered in the Archive Conversation System case study.

This keeps the document focused on retrieval, not on every possible future memory feature.

---

## System Boundary

```text
AI Client requests context
↓
Invocation Interface
↓
Orchestration Layer
↓
Context Layer
↓
Data Layer
↓
Structured context response
↓
AI Client continues work
```

The AI client can request context, but it does not own the archive state.

The invocation interface defines the controlled request boundary into Weft.

The orchestration layer controls the retrieval workflow.

The context layer shapes retrieved archive content into a usable response.

The data layer provides access to stored archive records.

The structured response goes back to the AI client so the user can continue the work.

---

## Retrieval Model

Context continuity is enabled through two operations.

### Discovery

Used when the correct archive record is not yet known.

```text
query → archive search → matching records
```

Discovery returns candidate records. It does not reconstruct the full context.

### Retrieval

Used when the target record or search boundary is known.

```text
identifier or bounded query → context retrieval → ordered clean_text blocks
```

Retrieval returns stored archive content in a structured response shape.

---

## Retrieval Rules

The retrieval side follows these rules:

- retrieval should not modify stored records
- lookup outcomes must be handled explicitly
- zero, one and multiple results are valid retrieval states
- retrieved text should follow the stored archive structure
- AI clients receive context, but do not become the source of truth

The retrieval workflow should not guess beyond the search boundary. If a query returns multiple records, the response should make that visible instead of silently treating one result as the only relevant context.

---

## Dependency on Archive System

Context continuity depends on prior archive operations.

```text
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

The retrieval side returns stored context so the user can continue work in an AI client.

It does not automatically decide which records should be combined, summarized or promoted into project documentation. Those steps remain explicit user-controlled workflows.

This boundary is intentional: Weft focuses first on reliable archive retrieval before adding more autonomous memory behavior.

---

## Related

* [Archive Conversation System](../archive-conversation-system/)
* [Architecture Foundations](../../architecture/README.md)
* [Payload Contracts](../../contracts/payload-contract.md)
* [System Overview](../../architecture/system-overview.md)
* [Known Limitations](../../status/known-limitations.md)