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