# System Overview

This document introduces the overall architecture of Weft.

It explains how the major components work together without describing the internal behaviour of individual systems. Workflow logic, payload processing and implementation details are documented in their own canonical locations.

For the complete component model, see [`layer-model.md`](./layer-model.md).

---

# System Purpose

Weft is an archive-first context infrastructure for AI workflows.

Its purpose is to separate **temporary AI interactions** from **durable project context**.

Instead of relying on the conversation history of an AI client, selected conversations and workflow outputs are persisted as structured records that can be searched and retrieved later.

The current implementation uses:

- **Make** for orchestration
- **Notion** as the human-readable source of record

---

# High-Level Architecture

```text
                Client
        (ChatGPT / Claude / MCP)

                  │
                  ▼

        Invocation Interface

                  │
                  ▼

            Make Workflows

                  │
                  ▼

        Context Processing

                  │
                  ▼

          Notion Repository

                  │
                  ▼

        Retrieval on Request
```

The AI client is an entry point into the system.

The archive remains the source of record.

---

# Major Components

| Component | Responsibility |
|----------|----------------|
| Client Surface | Sends structured requests and receives responses. |
| Invocation Interface | Defines the public boundary between clients and Weft. |
| Orchestration | Routes execution and coordinates workflows. |
| Context Processing | Validates, normalizes and shapes archived information. |
| Source of Record | Stores archive records and their relations. |

Each component has one primary responsibility.

No component should silently assume responsibilities that belong elsewhere.

---

# Core Systems

The current implementation consists of two systems.

## Archive Conversation

Persists selected AI conversations and workflow outputs as structured archive records.

Its responsibilities include validation, normalization, archive creation, archive updates and relation management.

The archive identity invariant binds one canonical conversation ID to one canonical project key. A conflicting request is blocked without changing Project or Archive state. Project repair is permitted only when the stored key matches and the existing Archive has no valid linked Project.

See:

`systems/archive-conversation/`

---

## Context Retrieval

Searches archived records and retrieves persisted context for continued work.

Searching and retrieval are separate responsibilities.

Searching identifies candidate records.

Retrieval returns stored context.

See:

`systems/context-retrieval/`

---

# System Boundary

The repository distinguishes between public interfaces and internal implementation.

The public boundary consists of:

- payload contracts
- JSON schemas
- example requests
- example responses

Behind that boundary, Make coordinates workflow execution while Notion stores the persistent records.

Clients interact with the public interface rather than with the storage implementation directly.

---

# Provisioning Boundary

The runtime systems are instantiated from the canonical Make blueprints by the public [`installer`](../installer/). Provisioning is outside request handling: it discovers target resources, creates the required Make Data Structures and scenarios, replaces environment bindings structurally, verifies API read-back, and leaves scenarios inactive. It does not change the canonical workflow logic.

Notion template duplication, connection authorization, MCP exposure, activation, and runtime acceptance remain explicit human-controlled boundaries.

---

# Design Philosophy

Several architectural decisions shape the implementation.

- archive before reuse
- explicit workflow boundaries
- client-independent invocation
- stable record identity
- deterministic routing
- clear responsibility separation

These principles are described in detail in [`engineering-principles.md`](./engineering-principles.md).

---

# Relationship to the Rest of the Repository

This document introduces the overall architecture.

More detailed documentation is organized by responsibility.

| Topic | Canonical location |
|--------|--------------------|
| Component responsibilities | `layer-model.md` |
| Engineering decisions | `engineering-principles.md` |
| Archive implementation | `systems/archive-conversation/` |
| Retrieval implementation | `systems/context-retrieval/` |
| Public contracts | `contracts/` |
| JSON Schemas | `schemas/` |
| Runtime evidence | Stored with the owning system under `systems/` |
| Automated provisioning | `installer/` |

Each topic is documented once and referenced elsewhere where needed.
