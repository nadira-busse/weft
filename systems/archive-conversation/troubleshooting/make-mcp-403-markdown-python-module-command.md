# Make MCP 403 for Markdown-formatted `python -m` commands

## Symptom

Weft `archive_conversation` can return:

```text
403 Forbidden
https://mcp.make.com
```

before the Make scenario starts.

In the reproduced cases, no corresponding execution appeared in Make Scenario History.

## Verified behavior

Controlled tests established the following:

- `python -m ...` formatted as Markdown code → HTTP 403 before the Make scenario
- the same command without Markdown code formatting → PASS
- other fenced code blocks → PASS
- `python` by itself in a fenced code block → PASS
- `-m` by itself in a fenced code block → PASS
- `python --version` in a fenced code block → PASS
- a previously rejected full archive succeeded after only the Markdown code formatting around its `python -m ...` commands was removed
- exact retrieval of that full archive by `conversation_id` → PASS

The same issue and workaround were later reproduced in other real archive requests.

## Workaround

If an archive request fails with HTTP 403 from `https://mcp.make.com` and no Make execution is created:

1. Search the complete archive content for `python -m ...`.
2. Check whether the command is formatted as Markdown code, either with inline backticks or inside a fenced code block.
3. Remove only the Markdown code formatting around that command.
4. Preserve the command text exactly.
5. Do not summarize, truncate, rewrite, reorder, or otherwise modify the archive content.
6. Retry `archive_conversation`.

### Example

**Affected Markdown source — do not send:**

````text
```text
python -m nadira_os.mcp_server.http_server
```
````

**Working representation — send instead:**

```text
python -m nadira_os.mcp_server.http_server
```

The command itself is unchanged. Only its Markdown code formatting is removed.

## AI troubleshooting prompt

The following prompt was used successfully on a reproduced failure:

> ## Weft `archive_conversation` — known 403 check
>
> If a Weft archive fails with:
>
> ```text
> 403 Forbidden
> https://mcp.make.com
> ```
>
> and no execution appears in Make Scenario History, first check the content being archived for:
>
> `python -m ...`
>
> formatted as Markdown code, for example inside a fenced code block or between backticks.
>
> ### Verified behavior
>
> Controlled tests established that:
>
> - `python -m ...` in Markdown code formatting → HTTP 403 before the Make scenario
> - the same command without Markdown code formatting → PASS
> - other code fences work; code fences themselves are therefore not the problem
> - the full previously rejected archive succeeded after only the code formatting around the `python -m ...` commands was removed
> - retrieval of that full archive by `conversation_id` → PASS
>
> ### What to do
>
> 1. Search the complete content being archived for `python -m ...`.
> 2. Check whether the command is between backticks or triple-backtick code fences.
> 3. Remove only the Markdown code formatting around that command.
> 4. Do not change the command text itself.
> 5. Retry `archive_conversation`.
>
> Example:
>
> **DO NOT SEND:**
>
> ````text
> ```text
> python -m nadira_os.mcp_server.http_server
> ```
> ````
>
> **SEND INSTEAD:**
>
> ```text
> python -m nadira_os.mcp_server.http_server
> ```
>
> ### Scope
>
> This is an observed Make MCP ingress limitation. The request is rejected before `archive_conversation` executes. The underlying gateway rule has not been established.
>
> If the content does not contain a Markdown-formatted `python -m ...` command, do not assume this is the same issue. Investigate the 403 separately.

## Scope

The evidence supports the following:

- the HTTP 403 occurs before `archive_conversation` executes in the reproduced cases;
- Markdown-formatted `python -m ...` commands reproduce the issue;
- the same command content as plain text is accepted;
- removing only that Markdown formatting resolves the reproduced issue;
- the workaround has succeeded on complete real archive requests;
- exact retrieval after archiving has passed.

The exact Make MCP gateway rule that causes the rejection has not been established.

If an HTTP 403 occurs without a Markdown-formatted `python -m ...` command, treat it as a separate failure until evidence shows otherwise.
