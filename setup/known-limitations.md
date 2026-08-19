# Current Boundaries

## Weft behavior boundaries

- timezone behavior across workflows
- get_context exact-date route behavior
- get_context limit help vs enforced behavior
- record-level vs append-operation idempotency

## Make platform and export boundaries

- canonical exports retain source-environment IDs, which installer rebinds
- stale exported public interface metadata can occur
- UI-visible AI-provider connection remains manual

### Make MCP archive rejection for Markdown-formatted `python -m` commands

A reproducible interoperability issue has been observed when
`archive_conversation` is invoked through Make MCP at `https://mcp.make.com`.

Archive requests containing a `python -m ...` command formatted as Markdown
code can be rejected with HTTP `403 Forbidden` before the
`archive_conversation` scenario starts. In that case, no execution appears in
Make Scenario History.

The verified workaround is to preserve the command text unchanged, remove only
the Markdown code formatting around the affected `python -m ...` command, and
retry the archive request.

The behavior has been reproduced in controlled tests and in multiple real
archive requests. Previously rejected full archives completed successfully
after applying the workaround, and exact retrieval by `conversation_id` also
passed.

See
[`../systems/archive-conversation/troubleshooting/make-mcp-403-markdown-python-module-command.md`](../systems/archive-conversation/troubleshooting/make-mcp-403-markdown-python-module-command.md)
for diagnosis steps, reproduction evidence, and an AI-assisted troubleshooting
prompt.

The underlying Make MCP gateway rule has not been established.

## Installation and recovery boundaries

- installation is not zero-touch because platform authorization remains manual
- state loss after partial provisioning fails closed on scenario-name collisions
- no automatic destructive rollback

## Optional workflow boundary

- create_daily_log parser Data Structure residual

## Verification boundary

- current repository changes require fresh live acceptance of the final published revision

## Deferred hardening

- append/block idempotency
- blueprint metadata sanitizer