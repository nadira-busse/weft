# Weft — Full Regression Test Report: `archive_conversation` V4

**Scenario under test:** `archive_conversation V4 test scenario`
**MCP tool:** `archive_conversation (MCP tool)`
**Test suite:** V4
**Execution date:** 6 August 2026
**Repository purpose:** Weft regression evidence
**Result:** **PASSED at tool-response and defined manual side-effect verification levels for all seven regression routes**

> This report records the V4 regression run after the latest changes to `archive_conversation`. It separates observable MCP/Make responses from manual Notion checks so that the evidence remains reproducible and auditable. For publication, account-bound record IDs, Notion URLs, scenario/tool names, and numeric Make module labels have been replaced with deterministic synthetic or descriptive values; response fields and cross-test identity relationships are preserved.

---

## 1. Scope

The regression suite validates the core routing and data-integrity behavior of `archive_conversation`:

1. invalid required input is rejected;
2. a new project and archive record can be created;
3. an existing project can be reused for a new archive record;
4. an existing archive can be updated under the same project;
5. reassignment to a conflicting existing project is blocked;
6. a missing project can be recreated when the stored project key still matches;
7. a missing project cannot be replaced by a different requested project.

The suite also checks normalization and persistence of `conversation_id`, `conversation_title`, `project`, `project_key`, `summary`, `source`, `source_platform`, `priority`, `messages`, and project relations.

## 2. Evidence model

Each test contains two evidence layers:

- **Tool evidence** — the captured response returned by the MCP tool, with only account-bound identifiers sanitized as described above.
- **Defined manual side-effect verification** — the explicitly listed Notion/Make persistence, relation, normalization, and no-change assertions for each test.

A successful JSON response alone is not enough to prove database integrity. Every manual assertion defined in this report was completed and confirmed after the corresponding tool execution. These confirmations are limited to the listed assertions and do not claim that every theoretically possible side effect was inspected.

---

# 3. Test 1 — Reject whitespace-only `conversation_id`

## Purpose

Verify that a required identifier containing only whitespace is rejected before any write is performed.

## Request

```json
{
  "conversation_id": " ",
  "conversation_title": "Route V4 Test 1 - validation error",
  "project": "Route V4 Alpha",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:20:00+02:00",
  "end_time": "2026-08-06T18:25:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Manual archive_conversation route V4 regression test 1."
    }
  ],
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "highNormalHigh"
}
```

## Response

```json
{
  "status": "error",
  "conversation_id": "missing",
  "record_id": null,
  "notion_url": null,
  "error_type": "validation_error",
  "message": "missing or invalid required fields: conversation_id",
  "module": "validation_router",
  "timestamp": "2026-08-06T18:19:16.948+02:00"
}
```

## Manual checks

Verify that:

- no Archive record was created;
- no Project record was created;
- no Notion write occurred;
- `record_id` and `notion_url` remained `null`.

## Status

**PASSED at tool-response and defined manual side-effect verification levels**

All manual assertions defined for this regression test were verified and confirmed.

---

# 4. Test 2 — New project + new archive

## Purpose

Verify that a previously unknown project is created and that one new Archive record is created and linked to it.

## Request

```json
{
  "conversation_id": "route-v4-test-02-new-project-new-archive",
  "conversation_title": "Route V4 Test 2 - new project and new archive",
  "project": "Route V4 Alpha",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:20:00+02:00",
  "end_time": "2026-08-06T18:25:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Manual archive_conversation route V4 regression test 2."
    }
  ],
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "highNormalHigh"
}
```

## Response

```json
{
  "status": "success",
  "conversation_id": "route-v4-test-02-new-project-new-archive",
  "record_id": "00000000-0000-4000-8000-000000000002",
  "notion_url": "https://example.notion.site/route-v4-test-02-new-project-new-archive-00000000000040008000000000000002",
  "error_type": null,
  "message": "archived",
  "module": "archive_conversation",
  "timestamp": "2026-08-06T18:23:19.434+02:00"
}
```

## Manual checks

Verify that:

- exactly one Project record named `Route V4 Alpha` exists;
- its normalized project key is `route v4 alpha`;
- exactly one Archive record exists for `route-v4-test-02-new-project-new-archive`;
- the Archive record is linked to `Route V4 Alpha`;
- priority is normalized to `Normal`;
- source is stored as `chat`;
- model origin/source platform reflects ChatGPT;
- no duplicate Project or Archive record exists.

## Status

**PASSED at tool-response and defined manual side-effect verification levels**

All manual assertions defined for this regression test were verified and confirmed.

---

# 5. Test 3 — Existing project + new archive

## Purpose

Verify that an existing Project record is reused rather than duplicated when a new conversation is archived under the same project.

## Request

```json
{
  "conversation_id": "route-v4-test-03-existing-project-new-archive",
  "conversation_title": "Route V4 Test 3 - existing project and new archive",
  "project": "Route V4 Alpha",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:26:00+02:00",
  "end_time": "2026-08-06T18:31:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Manual archive_conversation route V4 regression test 3."
    }
  ],
  "summary": "Regression test 3 verifies that an existing project is reused while a new archive record is created and linked correctly.",
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "highNormalHigh"
}
```

## Response

```json
{
  "status": "success",
  "conversation_id": "route-v4-test-03-existing-project-new-archive",
  "record_id": "00000000-0000-4000-8000-000000000003",
  "notion_url": "https://example.notion.site/route-v4-test-03-existing-project-new-archive-00000000000040008000000000000003",
  "error_type": null,
  "message": "archived",
  "module": "archive_conversation.append_page",
  "timestamp": "2026-08-06T18:27:08.178+02:00"
}
```

## Manual checks

Verify that:

- `Route V4 Alpha` still exists exactly once as a Project record;
- the existing Project record was reused;
- the Project now has both V4 Test 2 and V4 Test 3 Archive records linked;
- exactly one Archive record exists for `route-v4-test-03-existing-project-new-archive`;
- the project relation points to `Route V4 Alpha`;
- `Project key = route v4 alpha`;
- priority is normalized to `Normal`;
- the summary is stored exactly as supplied;
- source and model origin are correct;
- no duplicate Project or Archive record exists.

## Status

**PASSED at tool-response and defined manual side-effect verification levels**

All manual assertions defined for this regression test were verified and confirmed.

---

# 6. Test 4 — Update existing archive under the same project

## Purpose

Verify that a known `conversation_id` can be updated when the requested project matches the stored project, without creating a duplicate Archive or Project record.

## Request

```json
{
  "conversation_id": "route-v4-test-03-existing-project-new-archive",
  "conversation_title": "Route V4 Test 4 - update existing archive same project",
  "project": "Route V4 Alpha",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:26:00+02:00",
  "end_time": "2026-08-06T18:31:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Route V4 regression test 4 updated content for the existing archive."
    }
  ],
  "summary": "Regression test 4 verifies that an existing archive record is updated under the same project without creating a duplicate project or archive record.",
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "highNormalHigh"
}
```

## Response

```json
{
  "status": "success",
  "conversation_id": "route-v4-test-03-existing-project-new-archive",
  "record_id": "00000000-0000-4000-8000-000000000003",
  "notion_url": "https://example.notion.site/route-v4-test-04-updated-archive-00000000000040008000000000000003",
  "error_type": null,
  "message": "archived",
  "module": "archive_conversation.append_page",
  "timestamp": "2026-08-06T18:30:48.867+02:00"
}
```

## Manual checks

Verify that:

- the Make run used the `Match - no conflict` route;
- `Route V4 Alpha` exists exactly once as a Project record;
- the Archive record exists exactly once;
- the Archive record ID remains `00000000-0000-4000-8000-000000000003`;
- the title changed to `Route V4 Test 4 - update existing archive same project`;
- the project relation remains `Route V4 Alpha`;
- `Project key = route v4 alpha`;
- the new summary replaced the previous summary;
- priority is normalized to `Normal`;
- no new Project or Archive record was created.

## Status

**PASSED at tool-response and defined manual side-effect verification levels**

All manual assertions defined for this regression test were verified and confirmed. This confirms reuse and update of the intended Archive record, preservation of project identity and relation, and absence of duplicate Archive or Project records according to the defined checks. It does not prove operation-level append idempotency or retry safety after a partial page-content append.

---

# 7. Test 5 — Existing archive + conflicting existing project

## Purpose

Verify that an Archive record already associated with `Route V4 Alpha` cannot be reassigned to a different existing project, `Route V4 Beta`.

## 7.1 Beta fixture request

```json
{
  "conversation_id": "route-v4-test-05-beta-fixture",
  "conversation_title": "Route V4 Test 5 - beta fixture",
  "project": "Route V4 Beta",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:41:00+02:00",
  "end_time": "2026-08-06T18:46:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Fixture for Route V4 regression test 5."
    }
  ],
  "summary": "Regression test 5 fixture creates a separate Beta project and archive so the conflict guard can be tested against the existing Alpha archive.",
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "normal"
}
```

## 7.2 Beta fixture response

```json
{
  "status": "success",
  "conversation_id": "route-v4-test-05-beta-fixture",
  "record_id": "00000000-0000-4000-8000-000000000005",
  "notion_url": "https://example.notion.site/route-v4-test-05-beta-fixture-00000000000040008000000000000005",
  "error_type": null,
  "message": "archived",
  "module": "archive_conversation",
  "timestamp": "2026-08-06T18:42:09.384+02:00"
}
```

## 7.3 Conflict request

```json
{
  "conversation_id": "route-v4-test-03-existing-project-new-archive",
  "conversation_title": "Route V4 Test 5 - existing project conflict",
  "project": "Route V4 Beta",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:26:00+02:00",
  "end_time": "2026-08-06T18:31:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "This content must not be appended because Route V4 Beta conflicts with the stored Route V4 Alpha project key."
    }
  ],
  "summary": "Regression test 5 verifies that an existing Alpha archive cannot be reassigned to the separate Beta project and that the request is blocked without changes.",
  "source": "chat",
  "source_platform": "claude",
  "priority": "low"
}
```

## 7.4 Conflict response

```json
{
  "status": "blocked",
  "conversation_id": "route-v4-test-03-existing-project-new-archive",
  "record_id": "00000000-0000-4000-8000-000000000003",
  "notion_url": "https://example.notion.site/route-v4-test-04-updated-archive-00000000000040008000000000000003",
  "error_type": "PROJECT_CONFLICT",
  "message": "Conversation exists under a different project; request blocked without changes.",
  "module": "archive_conversation.guard.project_key",
  "timestamp": "2026-08-06T18:42:22.427+02:00"
}
```

## Manual checks

Verify that:

- `Route V4 Alpha` exists exactly once as a Project record;
- `Route V4 Beta` exists exactly once as a Project record;
- the Beta fixture is linked only to Beta;
- the Test 4 Archive remains linked only to Alpha;
- the Test 4 title and summary remain unchanged;
- the conflict summary is not persisted;
- the conflict message is not appended to Full content;
- priority, source and model origin remain unchanged;
- no extra Archive record or Beta relation is created.

## Status

**PASSED at tool-response and defined manual side-effect verification levels**

All manual assertions defined for this regression test were verified and confirmed.

---

# 8. Test 6 — Missing project + matching stored project key

## Purpose

Verify that a missing Project record is recreated and relinked when the Archive still carries the matching stored project key.

## 8.1 Gamma fixture request

```json
{
  "conversation_id": "route-v4-test-06-missing-project-matching-archive",
  "conversation_title": "Route V4 Test 6 - gamma fixture",
  "project": "Route V4 Gamma",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:46:00+02:00",
  "end_time": "2026-08-06T18:51:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Fixture for Route V4 regression test 6."
    }
  ],
  "summary": "Regression test 6 fixture creates a Gamma project and archive so the missing-project recovery route can be tested after the project record is removed.",
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "normal"
}
```

## 8.2 Gamma fixture response

```json
{
  "status": "success",
  "conversation_id": "route-v4-test-06-missing-project-matching-archive",
  "record_id": "00000000-0000-4000-8000-000000000006",
  "notion_url": "https://example.notion.site/route-v4-test-06-gamma-fixture-00000000000040008000000000000006",
  "error_type": null,
  "message": "archived",
  "module": "archive_conversation",
  "timestamp": "2026-08-06T18:47:06.081+02:00"
}
```

## Fixture manipulation

`Route V4 Gamma` was deleted manually.

Confirmed precondition:

```text
Projects:
0 × Route V4 Gamma

Archive:
1 × route-v4-test-06-missing-project-matching-archive

Project relation:
empty

Project key:
route v4 gamma
```

The manually prepared precondition state above was verified and confirmed before the recovery request was executed.

## 8.3 Recovery request

```json
{
  "conversation_id": "route-v4-test-06-missing-project-matching-archive",
  "conversation_title": "Route V4 Test 6 - project recreated and archive updated",
  "project": "Route V4 Gamma",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:46:00+02:00",
  "end_time": "2026-08-06T18:51:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Route V4 regression test 6 content after recreating the matching project."
    }
  ],
  "summary": "Regression test 6 verifies that a missing Gamma project is recreated and relinked when the stored and requested project keys match.",
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "high"
}
```

## 8.4 Recovery response

```json
{
  "status": "success",
  "conversation_id": "route-v4-test-06-missing-project-matching-archive",
  "record_id": "00000000-0000-4000-8000-000000000006",
  "notion_url": "https://example.notion.site/route-v4-test-06-restored-archive-00000000000040008000000000000006",
  "error_type": null,
  "message": "archived",
  "module": "archive_conversation.append_page",
  "timestamp": "2026-08-06T18:50:06.491+02:00"
}
```

## Manual checks

Verify that:

- the Make run used `Archive has no linked Project`;
- `Route V4 Gamma` was recreated exactly once;
- the existing Archive was relinked to Gamma;
- `Project key = route v4 gamma`;
- the conversation ID still exists exactly once;
- the Archive record ID remains `00000000-0000-4000-8000-000000000006`;
- title and summary were updated;
- no duplicate Archive record exists.

## Status

**PASSED at tool-response and defined manual side-effect verification levels**

All manual assertions defined for this regression test were verified and confirmed, including the required precondition verification recorded above.

---

# 9. Test 7 — Missing original project + conflicting requested project

## Purpose

Verify fail-closed behavior when the Archive relation is empty, the stored key is `route v4 delta`, and the incoming request asks for `Route V4 Epsilon`.

## 9.1 Delta fixture request

```json
{
  "conversation_id": "route-v4-test-07-missing-project-conflict",
  "conversation_title": "Route V4 Test 7 - delta fixture",
  "project": "Route V4 Delta",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:53:00+02:00",
  "end_time": "2026-08-06T18:58:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "Fixture for Route V4 regression test 7."
    }
  ],
  "summary": "Regression test 7 fixture creates a Delta project and archive so the missing-project conflict route can be tested after the Delta project record is removed.",
  "source": "chat",
  "source_platform": "chatgpt",
  "priority": "normal"
}
```

## 9.2 Delta fixture response

```json
{
  "status": "success",
  "conversation_id": "route-v4-test-07-missing-project-conflict",
  "record_id": "00000000-0000-4000-8000-000000000007",
  "notion_url": "https://example.notion.site/route-v4-test-07-delta-fixture-00000000000040008000000000000007",
  "error_type": null,
  "message": "archived",
  "module": "archive_conversation",
  "timestamp": "2026-08-06T18:53:18.461+02:00"
}
```

## Fixture manipulation

`Route V4 Delta` was deleted manually.

Confirmed precondition:

```text
Projects:
0 × Route V4 Delta
0 × Route V4 Epsilon

Archive:
1 × route-v4-test-07-missing-project-conflict

Project relation:
empty

Project key:
route v4 delta
```

The manually prepared precondition state above was verified and confirmed before the conflict request was executed.

## 9.3 Conflict request

```json
{
  "conversation_id": "route-v4-test-07-missing-project-conflict",
  "conversation_title": "Route V4 Test 7 - conflicting requested project",
  "project": "Route V4 Epsilon",
  "extraction_type": "conversation",
  "start_time": "2026-08-06T18:53:00+02:00",
  "end_time": "2026-08-06T18:58:00+02:00",
  "message_count": 1,
  "messages": [
    {
      "role": "user",
      "content": "This content must not be appended because Route V4 Epsilon conflicts with the stored Route V4 Delta project key."
    }
  ],
  "summary": "Regression test 7 verifies that a missing Delta project cannot be replaced by a conflicting Epsilon project when the archive retains the stored Delta project key.",
  "source": "chat",
  "source_platform": "claude",
  "priority": "low"
}
```

## 9.4 Conflict response

```json
{
  "status": "blocked",
  "conversation_id": "route-v4-test-07-missing-project-conflict",
  "record_id": "00000000-0000-4000-8000-000000000007",
  "notion_url": "https://example.notion.site/route-v4-test-07-delta-fixture-00000000000040008000000000000007",
  "error_type": "PROJECT_CONFLICT",
  "message": "Conversation exists under a different project; request blocked without changes.",
  "module": "archive_conversation.guard.project_key",
  "timestamp": "2026-08-06T18:55:50.998+02:00"
}
```

## Manual checks

Verify that:

- the Make run used the conflict fallback route;
- `Route V4 Epsilon` was not created;
- `Route V4 Delta` remains absent;
- the Archive Project relation remains empty;
- `Project key = route v4 delta`;
- the title remains `Route V4 Test 7 - delta fixture`;
- the original fixture summary remains unchanged;
- the conflict summary was not stored;
- the conflict message was not appended to Full content;
- priority, source and model origin remain unchanged;
- the Archive record still exists exactly once;
- the Archive record ID remains `00000000-0000-4000-8000-000000000007`.

## Status

**PASSED at tool-response and defined manual side-effect verification levels**

All manual assertions defined for this regression test were verified and confirmed, including the required precondition verification recorded above.

---

# 10. Regression matrix

| Test | Behavior | Expected result | Observed result | Status |
|---|---|---|---|---|
| 1 | Invalid `conversation_id` | Reject before write | `validation_error` | **PASSED — both evidence levels** |
| 2 | New project + new archive | Create both | `success` | **PASSED — both evidence levels** |
| 3 | Existing project + new archive | Reuse project, create archive | `success` | **PASSED — both evidence levels** |
| 4 | Existing archive + same project | Update existing archive | `success`, same record ID | **PASSED — both evidence levels** |
| 5 | Existing archive + conflicting project | Block without mutation | `PROJECT_CONFLICT` | **PASSED — both evidence levels** |
| 6 | Missing project + matching key | Recreate and relink | `success`, same record ID | **PASSED — both evidence levels** |
| 7 | Missing project + conflicting key | Block without mutation | `PROJECT_CONFLICT` | **PASSED — both evidence levels** |

---

# 11. Behavior confirmed by V4

V4 demonstrates the intended routing model:

- invalid identity input is rejected before any write;
- a new conversation can create both its Project and Archive records;
- existing Project identity is reused rather than duplicated;
- a known conversation keeps the same Archive `record_id` during updates;
- a conversation cannot silently migrate to another project;
- a missing Project can be recreated when the stored canonical project key still matches;
- a mismatch between stored and requested project identity fails closed with `PROJECT_CONFLICT`.

The key invariant is:

```text
stored project key != requested project key
→ PROJECT_CONFLICT
→ no reassignment
```

---

# 12. Notes on internal Make module identifiers

Environment-specific Make module labels and numeric IDs in the captured responses have been replaced with stable descriptive identifiers such as `archive_conversation.append_page` and `archive_conversation.guard.project_key`. The original module IDs are not part of the public API contract and can change when the scenario is edited or imported.

The stable behavioral contract is defined by:

- response status;
- `error_type`;
- conversation identity;
- Archive record identity;
- project-key invariants;
- observable database state.

---

# 13. Final result

The V4 suite produced the expected MCP/Make response and passed every defined manual side-effect assertion for all seven route classes.

```text
Test 1 — PASSED at both evidence levels
Test 2 — PASSED at both evidence levels
Test 3 — PASSED at both evidence levels
Test 4 — PASSED at both evidence levels
Test 5 — PASSED at both evidence levels
Test 6 — PASSED at both evidence levels
Test 7 — PASSED at both evidence levels
```

All manual assertions listed for each test were completed and confirmed alongside the response JSON. The result proves the defined persistence and side-effect checks; it does not claim inspection of every theoretically possible side effect. In particular, Test 4 proves record-level reuse under the defined checks, not operation-level append idempotency after a partial failure.

---

# 14. Conclusion

`archive_conversation` V4 demonstrates the tested Weft behavior covered by this regression suite:

- deterministic conversation identity;
- controlled Project creation and reuse;
- preservation of Archive record identity on update;
- explicit Project conflict protection;
- safe recovery from a missing Project relation;
- fail-closed behavior when stored and requested project identity disagree.

The regression suite deliberately exercises failure paths as well as success paths. For Weft, reproducibility means more than proving that the happy path works. It also means proving that state remains protected when related Notion data is missing, deleted, or inconsistent.
