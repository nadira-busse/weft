# Start Here

This repository documents Weft, a running archive-first system for preserving AI project context.

I built it because important project context kept getting lost in temporary chats, workflow outputs and scattered notes. Weft stores selected conversations, decisions and workflow outputs as structured records that can be searched and reused later.

The current system is based on a real Make + Notion implementation.

Built and maintained by **Nadira Büsse**.

---

## One-Line Summary

The core idea is to take conversations, decisions and workflow outputs that matter, and turn them into records I can actually search back through later.

---

## If You Have 2 Minutes

Read:

1. [`README.md`](./README.md) — what Weft is and why I built it
2. [`proof/README.md`](./proof/README.md) — runtime proof and debugging evidence

---

## If You Have 10 Minutes

Add:

3. [`architecture/system-overview.md`](./architecture/system-overview.md) — how the system works
4. [`architecture/archive-conversation-flow.md`](./architecture/archive-conversation-flow.md) — the core archive flow
5. [`assets/screenshots/README.md`](./assets/screenshots/README.md) — runtime screenshots
6. [`patterns/README.md`](./patterns/README.md) — reusable workflow patterns from the implementation

---

## If You Want the Full Picture

Recommended reading order:

1. [`architecture/system-overview.md`](./architecture/system-overview.md)
2. [`architecture/layer-model.md`](./architecture/layer-model.md)
3. [`architecture/design-principles.md`](./architecture/design-principles.md)
4. [`architecture/archive-conversation-flow.md`](./architecture/archive-conversation-flow.md)
5. [`contracts/payload-contract.md`](./contracts/payload-contract.md)
6. [`schemas/`](./schemas/)
7. [`examples/public-contracts/`](./examples/public-contracts/)
8. [`patterns/`](./patterns/)
9. [`case-studies/`](./case-studies/)
10. [`proof/`](./proof/)
11. [`status/known-limitations.md`](./status/known-limitations.md)

---

## What Makes This Different

Most AI workflow examples focus on tools.

Weft focuses on the system around the tools:

* how context is captured
* how records are structured
* how archived context can support later work
* where the current system has limits

The proof directory contains runtime evidence from the implementation, including bugs I encountered and corrected while building the system.

See: [`proof/README.md`](./proof/README.md)
