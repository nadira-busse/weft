# Layer Model

The Layer Model defines the primary responsibility boundaries within Weft.

Its purpose is not to describe deployment layers or technology stacks. Instead, it separates the concerns of **workflow execution**, **context processing** and **persistent storage** so each part of the system has a clear and limited responsibility.

These boundaries make the implementation easier to understand, maintain and extend without introducing unnecessary coupling between workflows.

---

# Overview

Weft is organized into three logical layers.

```text
┌──────────────────────────────┐
│      Orchestration Layer     │
├──────────────────────────────┤
│      Context Layer           │
├──────────────────────────────┤
│        Data Layer            │
└──────────────────────────────┘
```

The layers represent responsibilities rather than technologies.

The current implementation uses Make and Notion, but the layer boundaries are technology-independent.

---

# Layer Responsibilities

## Data Layer

The Data Layer is the persistent source of record.

It stores structured information that must remain available after an AI conversation or workflow has ended.

Current examples include:

- archive records
- project records
- daily log records
- workflow error records
- record relationships

### Responsibilities

- persist structured records
- maintain stable identifiers
- preserve relationships
- support retrieval
- protect source content from unintended modification

### Does Not Do

The Data Layer does **not**:

- execute workflows
- normalize payloads
- determine routing
- shape runtime context
- apply business logic

---

## Context Layer

The Context Layer transforms stored information into a form that workflows and AI clients can use.

It sits between orchestration and storage.

Its responsibility is to make data usable without changing the underlying records.

### Responsibilities

- validate input structures
- normalize payloads
- retrieve archive content
- shape runtime context
- prepare structured responses

### Does Not Do

The Context Layer does **not**:

- store records
- decide workflow routing
- own workflow execution
- modify archive content unless explicitly requested by the workflow

---

## Orchestration Layer

The Orchestration Layer coordinates the system.

It determines **what happens next**, not **what the stored data means**.

In the current implementation this responsibility is fulfilled by Make workflows.

### Responsibilities

- receive requests
- trigger workflows
- coordinate execution
- control routing
- invoke system operations
- return structured responses
- handle operational failures

### Does Not Do

The Orchestration Layer does **not**:

- become the system of record
- duplicate storage logic
- reshape archive data directly
- bypass validation

---

# Responsibility Boundaries

Each responsibility exists once.

| Responsibility | Owning Layer |
|---------------|--------------|
| Workflow execution | Orchestration |
| Routing | Orchestration |
| Payload validation | Context |
| Payload normalization | Context |
| Runtime context shaping | Context |
| Archive persistence | Data |
| Relationship storage | Data |
| Stable record identity | Data |

Keeping ownership explicit reduces duplicated logic and makes workflow behaviour easier to reason about.

---

# Why These Boundaries Matter

The boundaries are the result of practical implementation experience rather than theoretical design.

Without clear separation, workflow systems gradually become responsible for everything:

- execution
- validation
- storage
- transformation
- routing
- retrieval

When these concerns become intertwined, workflows become harder to debug, harder to modify and easier to break.

Separating responsibilities keeps each part of the system focused on a single concern.

---

# Current Implementation

The current implementation maps these responsibilities as follows.

| Responsibility | Current implementation |
|---------------|------------------------|
| Workflow orchestration | Make |
| Context processing | Make modules and structured payload transformations |
| Persistent storage | Notion |

These technologies are implementation choices rather than architectural requirements.

The responsibility boundaries are documented separately from the current Make and Notion implementation.

---

# Relationship to the Architecture

This document defines **where responsibilities belong**.

The remaining architecture documents answer different questions.

| Question | Document |
|----------|----------|
| How does the complete system fit together? | `system-overview.md` |
| Why were these engineering decisions made? | `engineering-principles.md` |
| How does a specific system behave? | `systems/` |

Together these documents describe the architecture without duplicating the same explanations across the repository.