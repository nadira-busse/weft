# Weft — Archive-First Context Infrastructure for AI Workflows

Weft documents a running archive-first system for AI project context.

I built it because important project context kept getting lost in temporary chats, workflow outputs and scattered notes. When I wanted to continue later, I often had to reconstruct what had already happened: decisions, errors, next steps and project state.

Weft solves that by storing selected conversations, decisions and workflow outputs as structured records that can be searched, linked to projects and reused later.

The current system runs on Make and Notion. This repository shows the public architecture, contracts, schemas, examples, screenshots, proof cases, patterns and known limitations.

It does not publish my full private runtime setup.

---

## Summary

Weft saves selected AI conversations, decisions and workflow outputs in a structured way, so I can find and reuse them later.

The basic rule is simple: important context is saved first, and only reused after that.

---

## 10-Minute Reviewer Path

You do not need to read the whole repository to understand the project.

1. [`README.md`](./README.md) — what Weft is and why I built it
2. [`proof/README.md`](./proof/README.md) — runtime proof and debugging evidence
3. [`assets/screenshots/README.md`](./assets/screenshots/README.md) — runtime screenshots
4. [`status/known-limitations.md`](./status/known-limitations.md) — current boundaries and limitations

For technical review:

1. [`contracts/payload-contract.md`](./contracts/payload-contract.md)
2. [`schemas/`](./schemas/)
3. [`examples/public-contracts/`](./examples/public-contracts/)
4. [`patterns/`](./patterns/)
5. [`architecture/archive-conversation-flow.md`](./architecture/archive-conversation-flow.md)

---

## What Weft Solves

AI-assisted work often breaks down because useful context stays trapped in temporary places:

- chat histories
- workflow outputs
- scattered notes
- project updates
- decisions that were not stored properly

That creates practical problems:

- project context has to be reconstructed manually
- decisions become hard to find
- follow-up sessions do not reliably build on earlier work
- outputs are difficult to audit or reuse
- workflow errors are harder to trace
- context is not portable across tools or AI clients

Weft moves important context out of the chat and into an external archive.

The AI chat is not the place where the memory lives. The archive is.

---

## What I Built

I built a working archive-first system using Make and Notion.

The system can:

- archive AI conversations and workflow outputs
- normalize incoming content into structured payloads
- store archive records in Notion
- link records to projects and daily logs
- search archived work by project, date, query or conversation ID
- retrieve stored context for follow-up work
- record workflow errors for later diagnosis
- separate source content from summaries, metadata and derived views

Make handles orchestration. Notion is the current human-readable system of record.

AI clients and workflow clients can invoke the system if they send the expected payload shape.

---

## How It Works

A typical Weft flow:

```text
AI conversation / workflow output
↓
structured payload
↓
archive record
↓
project relation
↓
daily log relation
↓
retrievable context
↓
continued work
```

The core flows are:

### 1. Archive Conversation

Stores an AI interaction or workflow output as a structured archive record.

This flow validates incoming data, normalizes message content, creates or updates archive records, links records to projects and daily logs, and returns structured output to the caller.

See: [`architecture/archive-conversation-flow.md`](./architecture/archive-conversation-flow.md)

### 2. Search Archive

Searches existing archive records through defined routes:

- conversation ID
- project
- exact date
- date range
- query fallback

Search does not rebuild full context. It selects bounded archive candidates.

### 3. Get Context

Retrieves archived content for continued work.

Instead of relying only on AI-client memory, stored context is retrieved from persisted records.

---

## System Architecture

![Weft System Overview](diagrams/weft-system-overview.svg)

| Component           | Responsibility                                                                                    | Current implementation                            |
| ------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| AI / Client Surface | Sends input and receives output                                                                   | ChatGPT, Claude, MCP-enabled invocation, webhooks |
| Orchestration Layer | Routes workflows, runs scenarios, handles retries and returns output                              | Make                                              |
| Context Layer       | Shapes payloads, prepares relations, normalizes data and turns stored records into usable context | Make modules, JSON, variables                     |
| Data Layer          | Stores archive records, project relations, daily logs and error records                           | Notion                                            |

The important boundary is this:

AI clients can invoke Weft, but they do not own the stored context.

---

## Design Choices

| Design choice              | Why it matters                                                                        |
| -------------------------- | ------------------------------------------------------------------------------------- |
| Archive-first              | Important AI work is stored before it is reused, summarized or promoted elsewhere.    |
| Client-independent         | ChatGPT and Claude are clients, not the system core.                                  |
| Stable identifiers         | Duplicate archive records are avoided during retries or repeated workflow calls.      |
| Explicit payload contracts | Workflow boundaries are easier to inspect, test and correct.                          |
| Structured error logging   | Failures can be diagnosed later instead of disappearing inside Make run history.      |
| Notion as MVP storage      | The current storage layer is easy to inspect and useful at this stage of the project. |

Notion is a deliberate MVP trade-off. It is not presented as the best long-term storage backend for every use case.

Make has a rollback mechanism, but it doesn't apply to most Notion actions — if a scenario fails halfway, a partial write can stay in Notion. So I focused on what I could control: clear payloads, stable IDs, explicit routes and visible errors.

---

## Evidence in This Repository

You can verify:

- architecture model and workflow boundaries
- archive conversation flow
- payload contracts
- JSON schemas for request and response boundaries
- example payloads
- runtime screenshots
- debugging proof cases
- reusable workflow patterns
- known limitations

### Archive-first context flow

![Archive-First Context Flow](diagrams/archive-conversation-flow.svg)

This diagram shows how temporary AI interactions are converted into structured archive records and later retrieved as reusable context.

### Archive workflow run history

![Archive workflow run history](assets/screenshots/make-archive-conversation-run-history.png)

This screenshot shows repeated successful executions of the archive workflow.

Additional screenshots are documented in [`assets/screenshots/README.md`](./assets/screenshots/README.md).

### Runtime proof

The [`proof/`](./proof/) directory documents issues I ran into while building Weft, including:

- search contract stabilization
- date range filtering
- multi-result aggregation
- relation traversal and identifier mapping

These cases show where the workflow broke, what the root cause was and how I corrected it.

---

### End-to-End Demo: Cross-Model Context Transfer

This short walkthrough shows the full loop: archiving a conversation from ChatGPT into Notion through the `archive_conversation` scenario, the Make run completing successfully, and Claude retrieving the same archived context through `get_context`.

▶ [Watch the demo](https://youtu.be/980BhT4nMWc)

---

## Payload Contracts and Schemas

Weft uses fixed request and response shapes, so each workflow knows what input to expect and what output to return.

The repository includes examples and schemas for:

- archive conversation
- search archive
- get context

See:

- [`contracts/payload-contract.md`](./contracts/payload-contract.md)
- [`schemas/`](./schemas/)
- [`examples/public-contracts/`](./examples/public-contracts/)

---

### Validation Tooling

I keep a small [`scripts/`](./scripts/) folder with the tooling I use to keep this repository consistent. Both scripts are plain Python with no project-specific logic, so they are not tied to Make, Notion or Weft internals.

**Schema validation** — checks that the public example payloads still match their JSON Schemas:

```powershell
py .\scripts\validate_examples.py
```

```bash
python3 scripts/validate_examples.py
```

Install the required Python dependency first if needed:

```powershell
py -m pip install -r requirements.txt
```

```bash
python3 -m pip install -r requirements.txt
```

This validation checks the documented example payloads against their schemas. It does not validate the full runtime implementation.

**Internal link check** — scans every Markdown file in the repository and verifies that relative links resolve to a real file. No extra dependencies required:

```powershell
py .\scripts\check_internal_links.py
```

```bash
python3 scripts/check_internal_links.py
```

I run both before publishing changes to this repository.

---

## Pattern Library

The [`patterns/`](./patterns/) directory captures reusable workflow patterns from the implementation.

Examples include:

- explicit existence checks
- get-or-create upsert
- idempotent archive writes
- immutable field guards
- validation-before-lookup
- relation identifier mapping

These patterns came from problems I actually encountered while building the system.

They are included because they show how I think about workflow reliability, not because the system is finished or perfect.

---

## Scope and Limitations

Weft documents a working private implementation, but this repository is not a deployable open-source package or packaged SaaS product.

Private runtime configuration, credentials, internal identifiers, personal archive content and full Make and Notion setup details are intentionally excluded.

The current implementation uses Make and Notion as an MVP stack, with the trade-offs that come with those choices. Multi-user access, advanced permissioning, high-scale storage and production-grade observability are outside the current scope.

See [`status/known-limitations.md`](./status/known-limitations.md) for the detailed technical boundaries.

---

## Trade-Offs

| Decision                       | Benefit                                   | Cost                                 |
| ------------------------------ | ----------------------------------------- | ------------------------------------ |
| Archive-first design           | Context becomes easier to trace and reuse | More writes and relations            |
| Make as orchestration layer    | Fast iteration and visual debugging       | Less flexible than custom code       |
| Notion as MVP system of record | Human-readable and easy to inspect        | Not designed for high-scale storage  |
| Explicit routing               | More predictable workflow behavior        | More orchestration logic             |
| Client-independent inputs      | AI clients remain replaceable             | Requires stricter payload discipline |

---

## Repository Map

```text
.
├── architecture/          # Architecture model and workflow documentation
├── assets/screenshots/    # Runtime screenshots with sensitive details omitted
├── case-studies/          # Applied workflow case studies
├── contracts/             # Payload contract documentation
├── diagrams/              # System and workflow diagrams
├── examples/              # Example payloads
├── patterns/              # Reusable workflow patterns
├── proof/                 # Runtime proof and debugging evidence
├── schemas/               # JSON schemas for payload boundaries
├── scripts/               # Validation tooling: schema checks and internal link checks
├── status/                # Known limitations and system status
├── START-HERE.md
├── SYSTEM-IN-PRODUCTION.md
├── requirements.txt
└── README.md
```

---

## About

Built by **Nadira Büsse**.

LinkedIn: [linkedin.com/in/nadirabusse](https://www.linkedin.com/in/nadirabusse)

I build AI-assisted workflow systems because I want to understand how context, automation and structured records work together in practice.

Weft is one of the projects I use to show how I think and work: I start from a real workflow problem, build a working system, test where it breaks, document the trade-offs, and improve it from there.
