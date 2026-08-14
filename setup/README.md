# Setup References

The canonical end-to-end guide for a first installation is [`../SETUP.md`](../SETUP.md). Follow that guide from beginning to end.

This directory contains supporting technical references, not a second installation tutorial. Use an individual document when you need implementation detail beyond the main guide:

| Reference | Independent role |
|---|---|
| [`notion/README.md`](./notion/README.md) | Notion model relationships and template distribution |
| [`notion/database-schema.md`](./notion/database-schema.md) | Exact Notion database properties and formulas |
| [`data-structure.md`](./data-structure.md) | Installer-created Make Data Structure definitions and bindings |
| [`make-provisioning.md`](./make-provisioning.md) | Make provisioning, read-back, reporting, and recovery behavior |
| [`connections.md`](./connections.md) | Connection families, scopes, dependency bindings, and MCP exposure |
| [`verification.md`](./verification.md) | Evidence categories and acceptance checks |
| [`known-limitations.md`](./known-limitations.md) | Current verified limitations and deferred hardening |

The public installer entrypoint is `python -m installer`; its command behavior is summarized in [`../installer/README.md`](../installer/README.md). Canonical blueprints live in [`Make/blueprints/`](./Make/blueprints/); target-environment IDs must never be written back into those public files.
