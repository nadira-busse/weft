# Design Principles

These principles describe how Weft workflows are expected to behave.

They are not abstract architecture rules. They came from problems I ran into while building the system: duplicate records, unclear routing, unstable identifiers, hidden transformations and workflow errors that were hard to trace.

The goal is to keep the system predictable, reviewable and safe to retry within the constraints of Make and Notion.

---

## Predictable Workflows

Workflows should behave predictably for the same validated input.

This requires:

* clear input and output structures
* explicit routing conditions
* no hidden state inside the workflow
* defined handling for zero, one or multiple matching records
* visible failure paths

The goal is not to claim perfect determinism under every possible condition.

The goal is to make workflow behavior understandable and repeatable enough to inspect, debug and improve.

---

## Idempotent Operations

Operations that may be retried must be safe to run more than once.

Repeated execution should not create:

* duplicate archive records
* conflicting relations
* unintended side effects
* inconsistent project or daily-log links

Weft uses stable identifiers, existence-first checks and controlled update behavior to reduce that risk.

This matters most in archive workflows, where the same conversation or workflow output may be submitted again after a retry or failed execution.

---

## Separation of Concerns

Weft separates responsibilities across three layers:

* **Data Layer** — stores archive records and relations
* **Context Layer** — shapes stored records into usable context
* **Orchestration Layer** — controls workflow execution and routing

Each layer has a specific job.

This prevents storage, transformation and execution logic from becoming mixed into one hard-to-debug workflow.

See: [`layer-model.md`](./layer-model.md)

---

## Stable Identity and Schema Discipline

Workflow reliability depends on stable identity and clear data structures.

Weft uses:

* stable identifiers for archive records and relations
* schemas for public payload boundaries
* required fields where missing data would break the flow
* controlled update rules for fields that should not change silently
* explicit relation mapping before write operations

This protects the archive from common workflow problems such as duplicate records, missing relations and inconsistent payload shapes.

---

## Observable Workflows

Workflow behavior should be traceable.

A reviewer or maintainer should be able to see:

* which route ran
* which input was used
* which record was created or updated
* where a failure happened
* whether the issue was a workflow error, mapping issue or data issue

Weft keeps error logging separate from normal archive records because execution failures should not be mixed with archived source content.

---

## Composable Workflow Design

Weft uses smaller workflow components where that makes the system easier to maintain.

A component should have:

* one main responsibility
* clear inputs
* clear outputs
* reusable behavior
* visible failure modes

This is why supporting logic, such as Notion block text extraction, can live in a separate subscenario instead of being duplicated inside every workflow.

Composable design is useful only when it reduces complexity. If splitting a workflow makes the system harder to understand, it is not an improvement.

---

## Why These Principles Matter

These principles help keep Weft from turning into a collection of disconnected automations.

They protect against:

* duplicated logic
* unclear source-of-truth boundaries
* hidden data transformations
* unstable identifiers
* workflow retries that create inconsistent state
* errors that disappear inside Make run history

There's no guarantee nothing ever goes wrong.

What I do get is this: when something breaks, I can usually see where and why fairly quickly.
