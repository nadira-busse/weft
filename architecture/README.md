# Architecture

This folder documents the architecture behind Weft.

It explains how the system separates storage, context shaping and workflow execution, and how archived AI context moves through the system.

For the general project overview, start with [`../README.md`](../README.md).

---

## Documents

| Document                                                         | Purpose                                                                                |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| [`layer-model.md`](./layer-model.md)                             | Explains the Data, Context and Orchestration layers.                                   |
| [`design-principles.md`](./design-principles.md)                 | Describes the principles used to keep workflows predictable, traceable and reviewable. |
| [`archive-conversation-flow.md`](./archive-conversation-flow.md) | Shows the public architecture of the main archive workflow. |
| [`system-overview.md`](./system-overview.md) | Gives a short orientation to how the Weft system fits together. |                       

---

## Reading Order

Recommended order:

1. [`system-overview.md`](./system-overview.md)
2. [`layer-model.md`](./layer-model.md)
3. [`design-principles.md`](./design-principles.md)
4. [`archive-conversation-flow.md`](./archive-conversation-flow.md)

Related sections:

* [`../contracts/`](../contracts/)
* [`../schemas/`](../schemas/)
* [`../patterns/`](../patterns/)
* [`../proof/`](../proof/)
