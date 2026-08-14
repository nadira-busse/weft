# Public JSON Schemas

The three public MCP scenarios use one request schema and one response schema each:

- [`archive-conversation/`](./archive-conversation/)
- [`search-archive/`](./search-archive/)
- [`get-context/`](./get-context/)

These schemas describe client payloads. They are separate from Make Data Structures and from the public input/output specifications embedded in exported scenarios. Run `python scripts/validate_examples.py` from the repository root to validate the schemas, public examples, all seven current Archive V4 regression suites and their JSON fixtures, and blueprint output specifications. The canonical regression evidence is the [V4 regression report](../regression-tests/Weft_full_regression_test_report_archive_conversation_V4.md).
