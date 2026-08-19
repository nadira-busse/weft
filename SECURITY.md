# Security Policy

## Reporting a vulnerability

If you find a potential security issue in Weft, please do not open a public GitHub issue.

Use GitHub Private Vulnerability Reporting for this repository instead.

When reporting a vulnerability, include where possible:

- a short description of the issue;
- the affected file, component, workflow or setup step;
- reproduction details;
- the potential impact;
- any relevant environment or configuration context.

## Project scope

Weft is a public Apache-2.0-licensed reference implementation and portfolio project.

It is not operated as a hosted production service for third-party users.

The repository demonstrates archive, retrieval, installer and workflow patterns across Make, Notion and MCP-oriented integrations. Security of a self-hosted or reproduced deployment also depends on the operator's own:

- Make account and API-token configuration;
- Notion workspace and integration permissions;
- MCP client configuration;
- credential storage;
- access controls;
- external platform settings.

Do not include secrets, API keys, tokens, passwords or other credentials in a vulnerability report.

## Supported version

Security fixes, where applicable, target the current repository state on the default branch.

Older revisions and independently modified deployments are not separately maintained.

## Response expectations

No response-time, remediation-time or support SLA is provided.

Reports will be reviewed when possible, and confirmed repository issues may be addressed according to their severity, reproducibility and the current maintenance scope of the project.
