# Public Contract Examples

Each scenario directory contains schema-valid request and response fixtures. Files ending in `.invalid.json` are expected failures and are asserted by `scripts/validate_examples.py`. The Archive examples include whitespace validation, success, and side-effect-free project-conflict responses.

- [`archive-conversation/`](./archive-conversation/)
- [`search-archive/`](./search-archive/)
- [`get-context/`](./get-context/)

All values are sanitized examples. They are not deployment identifiers or private archive content.
