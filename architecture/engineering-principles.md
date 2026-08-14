# Engineering Principles

The engineering principles in this document describe **how Weft is designed to behave**, not how every workflow is implemented.

They are based on practical problems encountered while building the system, including duplicate archive records, inconsistent routing, unstable identifiers, hidden data transformations and difficult-to-diagnose workflow failures.

These principles provide the engineering rules that guide the implementation across the repository.

---

# Archive-First

Weft is built around a simple rule:

> Important context is archived before it is reused.

Once context has been persisted, later workflows retrieve the archived record rather than relying on temporary AI conversation history.

This creates an explicit separation between transient interactions and durable project context.

---

# Explicit Boundaries

Every workflow exposes a clearly defined request and response boundary.

Clients interact with those public contracts rather than with the underlying implementation.

This separation makes workflows easier to:

- understand
- validate
- test
- maintain
- replace

Public payload contracts are documented separately from internal workflow implementation.

---

# Stable Identity

Every archive record represents one logical interaction.

Repeated accepted archive requests for the same stable conversation identity converge on the same Archive record instead of creating additional records. The workflow implements this record-level idempotency through explicit lookup and create-or-update routing; a request that conflicts with the stored project identity is blocked rather than creating another Archive record.

Stable identifiers make archive operations predictable and reduce duplicate Archive records during retries or repeated requests.

---

# Existence-First Writes

Archive workflows determine whether the target record already exists before deciding between creation and update.

This approach keeps write behaviour explicit and avoids relying on implicit platform behaviour.

The responsibility for deciding whether a record should be created or updated belongs to the workflow itself.

---

# Scoped Idempotency

Record-level idempotency does not imply operation-level idempotency.

Weft currently distinguishes between:

- **Record-level idempotency:** repeated accepted requests for the same stable conversation identity use explicit lookup and update routing to converge on the same Archive record.
- **Operation-level append idempotency:** page-content append operations are not fully idempotent. If an append succeeds but the run fails before returning successfully, retrying the request can append the same body blocks again even though the existing Archive record is reused.

Operation-level or block-level append idempotency is a separate future hardening concern, not a current release blocker for the record-level guarantee. The limitation is tracked in [`../setup/known-limitations.md`](../setup/known-limitations.md).

---

# Deterministic Routing

Workflow execution follows explicit routing decisions.

The same validated input should follow the same execution path unless external data has changed.

Deterministic routing improves:

- predictability
- debugging
- reproducibility
- maintenance

It does not guarantee identical outcomes under every possible runtime condition.

---

# Separation of Responsibilities

Storage, context processing and workflow execution are treated as separate concerns.

The architecture therefore distinguishes between:

- Data Layer
- Context Layer
- Orchestration Layer

Each layer owns one primary responsibility.

This prevents storage logic, transformation logic and execution logic from gradually merging into a single workflow.

See:

`layer-model.md`

---

# Explicit Transformations

Data transformations should always be visible.

Payload shaping, normalization and formatting belong to the Context Layer rather than being hidden inside storage operations or workflow routing.

Making transformations explicit improves traceability and simplifies debugging.

---

# Observable Behaviour

When a workflow succeeds or fails, it should be possible to determine:

- which route executed
- which request was received
- which record was processed
- where execution stopped
- whether the issue originated from validation, mapping, routing or storage

The objective is not to eliminate failures.

The objective is to make failures understandable.

---

# Client Independence

AI clients are treated as interchangeable entry points into the system.

The archive remains independent of any individual client.

This allows the same archive to be used through different invocation methods without changing the underlying archive model.

---

# Source Before Derived Data

Source records remain the authoritative representation of archived interactions.

Derived information such as summaries, metadata or navigation fields may support retrieval, but they do not replace the archived source record.

Separating source content from derived information keeps archive behaviour easier to reason about and reduces the risk of unintentionally modifying historical records.

---

# Engineering Trade-Offs

The current implementation intentionally favours clarity over optimisation.

Examples include:

- explicit routing instead of implicit behaviour
- visible validation instead of silent correction
- structured payloads instead of loosely defined inputs
- readable workflows instead of maximum compactness

These choices sometimes introduce additional workflow steps, but they make the implementation easier to inspect, reproduce and maintain.

---

# Relationship to the Architecture

This document explains **why** the implementation follows certain engineering decisions.

The remaining architecture documents answer different questions.

| Question | Document |
|----------|----------|
| What does the system look like? | `system-overview.md` |
| Where do responsibilities belong? | `layer-model.md` |
| How do individual systems behave? | `systems/` |

Together these documents define the architectural foundation of Weft without duplicating implementation details.
