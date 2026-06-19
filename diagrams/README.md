# Diagrams

This directory contains visual diagrams for the Weft architecture.

The diagrams are orientation assets. They show system boundaries, main workflow paths and responsibility areas. Detailed explanations are documented in the architecture, case studies, contracts and proof directories.

---

## Diagrams

| Diagram                                                            | Purpose                                                                                                          |
| ------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| [`weft-system-overview.svg`](./weft-system-overview.svg)           | High-level system architecture: AI clients, workflow invocation, orchestration, storage and retrieval boundaries |
| [`archive-conversation-flow.svg`](./archive-conversation-flow.svg) | Archive-first context flow: how AI interactions become persistent, retrievable working context                   |

---

## Reading Order

Start with:

1. [`../README.md`](../README.md)
2. [`../architecture/system-overview.md`](../architecture/system-overview.md)
3. [`../architecture/layer-model.md`](../architecture/layer-model.md)
4. [`../case-studies/archive-conversation-system/`](../case-studies/archive-conversation-system/)

---

## Publication Note

The diagrams show public architecture boundaries, not private implementation detail.

Implementation-specific workflow logic, Make mappings, private database structures, internal identifiers and sensitive runtime data are intentionally omitted.
