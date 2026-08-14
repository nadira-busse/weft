# Architecture

The `architecture/` directory defines the system-wide design of Weft.

Its purpose is to explain **how the system is structured**, **why responsibilities are separated the way they are**, and **which engineering principles guide the implementation**.

It intentionally stays at the architectural level.

Workflow-specific behaviour, implementation details and runtime evidence are documented in the system that owns them rather than being repeated here.

For an introduction to the project, start with the repository [`README.md`](../README.md).

---

# Architecture Documents

| Document | Responsibility |
|----------|----------------|
| [`system-overview.md`](./system-overview.md) | Introduces the overall architecture and explains how the major components fit together. |
| [`layer-model.md`](./layer-model.md) | Defines the responsibility boundaries between orchestration, context processing and persistent storage. |
| [`engineering-principles.md`](./engineering-principles.md) | Describes the engineering decisions that make the implementation predictable, reproducible and maintainable. |

---

# What Belongs Here

The architecture documentation answers questions such as:

- What is the overall system boundary?
- Which responsibilities belong to each component?
- Why were those boundaries chosen?
- Which engineering principles guide the implementation?

These documents intentionally avoid explaining individual workflows in detail.

---

# What Does Not Belong Here

The following topics have their own canonical location elsewhere in the repository.

| Topic | Canonical location |
|--------|--------------------|
| Archive workflow behaviour | `systems/archive-conversation/` |
| Context retrieval behaviour | `systems/context-retrieval/` |
| Public request and response contracts | `contracts/` |
| JSON Schemas | `schemas/` |
| Example payloads | `examples/` |
| Runtime evidence | `systems/archive-conversation/assets/` and `systems/context-retrieval/` |
| End-to-end installation | `SETUP.md` |
| Supporting setup references | `setup/` |
| Automated Make provisioning | `installer/` |

Keeping these subjects separate prevents the same information from being maintained in multiple places.

---

# Architectural Scope

The architecture describes the current implementation.

It does not attempt to define a generic framework for AI systems or prescribe one correct way of building workflow automation.

Instead, it explains the design decisions behind a working archive-first implementation built with Make and Notion.

Where implementation-specific trade-offs exist, they are documented explicitly rather than presented as universal best practices.

---

# Reading Order

For most readers the recommended order is:

1. `system-overview.md`
2. `layer-model.md`
3. `engineering-principles.md`

The remaining repository documentation builds on these architectural concepts without redefining them.
