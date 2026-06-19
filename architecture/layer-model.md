# Layer Model

## Overview

Weft separates storage, context shaping and workflow execution into three layers.

The goal is to keep responsibilities clear:

* stored records belong in the **Data Layer**
* transformation belongs in the **Context Layer**
* workflow execution belongs in the **Orchestration Layer**

This prevents one workflow from silently becoming responsible for everything: storage, logic, routing, retries and context reconstruction.

---

## Model

```text
Orchestration Layer
↓
Context Layer
↓
Data Layer
```

Lower layers are more stable and persistent.

Upper layers can change more often, as long as they respect the boundaries of the layers below them.

---

## 1. Data Layer

The Data Layer is the archive system of record.

It stores structured records such as:

* source records — complete archived interactions or workflow outputs
* curated records — selected reusable knowledge
* derived records — summaries, metadata and navigation fields

### Responsibilities

* store structured records
* preserve stable identifiers
* keep relations consistent
* support retrieval
* protect stored source content from implicit changes

### Invariants

* each record must have a stable identifier
* source records preserve what happened, but are not automatically canonical knowledge
* reusable knowledge requires explicit extraction, selection or promotion
* stored data must not be changed implicitly
* write behavior must be defined per workflow

### Current implementation

* Notion archive database
* Notion project relations
* Notion daily log relations
* Notion error log records

---

## 2. Context Layer

The Context Layer turns stored records into usable context.

It is responsible for shaping data before it is used by a workflow or AI client.

### Responsibilities

* retrieve structured records
* normalize data formats
* assemble context for later use
* enforce expected input and output shapes

### Invariants

* identical stored input should produce the same context output
* transformations must be explicit and reproducible
* context generation must not create or mutate stored records
* formatting logic does not belong in the Data Layer

### Current implementation

* Make modules
* JSON payload shaping
* Notion block text extraction
* context assembly for `get_context`

---

## 3. Orchestration Layer

The Orchestration Layer controls workflow execution.

It decides which route runs, which checks happen first and how failures are handled.

### Responsibilities

* trigger workflows
* route execution
* handle retries
* call system operations
* return structured responses
* capture execution failures

### Invariants

* execution paths must be explicit
* retries must not create duplicate archive records
* workflows must operate on validated inputs
* orchestration does not own stored data
* workflow errors must remain observable

### Current implementation

* Make scenarios
* MCP-enabled invocation
* webhook-based execution
* archive/search/retrieval workflows

---

## Layer Interaction

The layers work together in this order:

1. **Data Layer** stores structured records.
2. **Context Layer** turns stored records into usable context.
3. **Orchestration Layer** executes workflows using validated inputs and assembled context.

Each layer consumes the output of the layer below it.

A workflow should not bypass the Context Layer to reshape stored data informally, and the Context Layer should not silently mutate the Data Layer.

---

## Why This Model Matters

This model exists because workflow systems become fragile when responsibilities blur.

The problems I wanted to avoid were:

* duplicate logic in multiple scenarios
* hidden data transformations
* unclear source-of-truth boundaries
* workflow retries creating inconsistent state
* tightly coupled Make modules that are hard to debug
* AI clients depending on chat memory instead of stored context

The layer model keeps the system easier to inspect, explain and change.

---

## Related Sections

* [Architecture](./README.md)
* [Archive Conversation Flow](./archive-conversation-flow.md)
* [Design Principles](./design-principles.md)
* [System Overview](./system-overview.md)
* [Patterns](../patterns/)
* [Proof](../proof/)
