# Notion Model Reference

Notion provides the canonical data model for Weft.

The reference implementation contains four core databases:

- Archive
- Projects
- Daily Log
- Error Logs


The Make scenarios read from and write to the core databases. The public template is linked and duplicated through the canonical first-time guide, [`../../SETUP.md`](../../SETUP.md).

## Template distribution

The current Weft template reproduced correctly in clean-install testing. If a duplicated Notion database does not behave as described, check its relations and workspace permissions before troubleshooting the installer.

## Database relationships

The Notion data model uses the following relationships:

```text
Archive
├─ Project → Projects
└─ Daily log → Daily Log

Projects
└─ Archive entries → Archive

Daily Log
└─ Archive entries → Archive

Error Logs
└─ No database relations
```

The `Projects` property in Daily Log is a rollup derived through the related archive entries. It is not a direct database relation.

## Schema

See [`database-schema.md`](./database-schema.md) for the included databases, properties and formulas.

## Template status

* **Template version:** v1.0
* **Last verified:** 2026-08-06
