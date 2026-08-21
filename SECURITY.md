# Security Policy

## Reporting a vulnerability

If you find a potential security issue in Weft, do not open a public GitHub issue.

Use GitHub Private Vulnerability Reporting for this repository instead.

When reporting an issue, include where possible:

* a short description of the problem
* the affected file, workflow, component or setup step
* steps to reproduce it
* the potential impact
* any relevant environment or configuration details

Do not include secrets, API keys, tokens, passwords or other credentials in the report.

## Scope

Weft is distributed under the Apache-2.0 license and is not operated as a hosted service.

A Weft installation uses resources and credentials in the user's own Make, Notion and MCP client environment. Security therefore also depends on how those accounts and integrations are configured, including:

* Make account, connection and API credentials
* Notion workspace and integration permissions
* MCP client authorization and local credential handling

Issues in Weft's repository, installer, workflows, schemas or documented setup are within the scope of this security policy.

Issues caused only by a user's own account permissions, credentials or third-party platform configuration are outside the repository's direct control.

## Supported version

Security fixes target the current repository state on the default branch.

Older revisions and independently modified deployments are not separately maintained.
