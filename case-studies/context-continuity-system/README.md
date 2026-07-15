# Case Study — Context Continuity System

The Context Continuity System describes the retrieval side of Weft.

It makes selected archive records searchable and retrievable across sessions, AI clients and workflow tools.

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

The objective is to return stored context through explicit search and retrieval workflows with stable identifiers and controlled response shapes.

The system does not try to make an AI client remember everything. It makes selected archived context available again when needed.

This is a controlled archive-and-retrieval layer, not full autonomous memory.

---

## Scope

This case study covers finding archived records and returning stored content in a structured response.

The archive write path is documented separately in the [Archive Conversation System](../archive-conversation-system/) case study.

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

The request moves through the invocation and orchestration boundaries before stored archive content is retrieved and shaped into a structured response.

The AI client receives that response, but it does not own or modify the archived source state.

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

The retrieval workflow should not guess beyond the search boundary. Multiple matches must remain visible instead of being silently reduced to one record.

---

## Current Boundary

Weft retrieves stored archive content but does not automatically decide which records should be combined, summarized or promoted into project documentation. See [`status/known-limitations.md`](../../status/known-limitations.md) — "Limited Context Composition."

Those steps remain explicit, user-controlled workflows.

---

## Related

* [Archive Conversation System](../archive-conversation-system/)
* [Architecture Foundations](../../architecture/README.md)
* [Payload Contracts](../../contracts/payload-contract.md)
* [System Overview](../../architecture/system-overview.md)
* [Known Limitations](../../status/known-limitations.md)