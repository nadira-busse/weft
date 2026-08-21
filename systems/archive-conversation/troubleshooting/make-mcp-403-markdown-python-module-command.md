# Make MCP 403 for Markdown-formatted `python -m` commands

## Symptom

Weft `archive_conversation` can return:

```text
403 Forbidden
https://mcp.make.com
```

before the Make scenario starts. In the reproduced cases, no corresponding execution appeared in Make Scenario History.

## What the tests showed

Controlled tests established that:

- `python -m ...` formatted as Markdown code produced HTTP 403 before the Make scenario started;
- the same command without Markdown code formatting passed;
- other fenced code blocks passed;
- `python`, `-m` and `python --version` separately passed in fenced code blocks;
- a previously rejected full archive succeeded after only the Markdown formatting around its `python -m ...` commands was removed;
- exact retrieval of that archive by `conversation_id` passed.

The same behavior and workaround were later reproduced in other complete archive requests.

## Workaround

If an archive request fails with HTTP 403 from `https://mcp.make.com` and no Make execution appears:

1. Search the complete archive content for `python -m ...`.
2. Check whether the command is between inline backticks or inside a fenced code block.
3. Remove only the Markdown code formatting around that command.
4. Keep the command text and all other archive content unchanged.
5. Retry `archive_conversation`.

### Example

Before removing the Markdown code formatting:

````text
```text
python -m nadira_os.mcp_server.http_server
```
````

After removing the formatting:

```text
python -m nadira_os.mcp_server.http_server
```

The command itself is unchanged.

## Scope

The evidence shows that the reproduced requests were rejected before `archive_conversation` executed and that removing only this formatting allowed them to pass. The underlying Make MCP gateway rule is unknown.

If an HTTP 403 occurs without a Markdown-formatted `python -m ...` command, investigate it separately rather than assuming it is the same issue.
