"""Local configuration discovery for the public installer."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

from dotenv import dotenv_values

from .clients import MakeClient
from .errors import InstallerError

ZONE_PATTERN = re.compile(r"^[a-z]{2,4}\d+$", re.IGNORECASE)
GENERATED_KEYS = ("MAKE_API_BASE_URL", "MAKE_ORGANIZATION_ID", "MAKE_TEAM_ID")


def make_base_url(zone: str) -> str:
    normalized = zone.strip().casefold()
    if not ZONE_PATTERN.fullmatch(normalized):
        raise InstallerError(
            "MAKE_ZONE must look like eu1, eu2, us1, or us2",
            code="INVALID_CONFIGURATION",
            config_key="MAKE_ZONE",
            action="Copy .env.example to .env and enter the zone shown at the start of your Make URL.",
            retry_safe=True,
        )
    return f"https://{normalized}.make.com/api/v2"


def load_bootstrap(env_file: Path) -> tuple[str, str, str]:
    if not env_file.exists():
        raise InstallerError(
            f"Environment file not found: {env_file}",
            code="MISSING_CONFIGURATION",
            action="Copy .env.example to .env, then add MAKE_ZONE, MAKE_API_TOKEN, and NOTION_INSPECT_TOKEN.",
            retry_safe=True,
        )
    values = {key: str(value or "").strip() for key, value in dotenv_values(env_file).items()}
    required = ("MAKE_ZONE", "MAKE_API_TOKEN", "NOTION_INSPECT_TOKEN")
    missing = [key for key in required if not values.get(key)]
    if missing:
        raise InstallerError(
            f"Missing required bootstrap configuration: {', '.join(missing)}",
            code="MISSING_CONFIGURATION",
            action="Add the missing private values to .env. The installer never writes or prints tokens.",
            retry_safe=True,
        )
    return values["MAKE_ZONE"], values["MAKE_API_TOKEN"], values["NOTION_INSPECT_TOKEN"]


def _choose(records: list[dict], label: str, input_fn: Callable[[str], str], output_fn: Callable[[str], None]) -> dict:
    valid = [item for item in records if isinstance(item.get("id"), int) and str(item.get("name") or "").strip()]
    if not valid:
        raise InstallerError(
            f"No accessible Make {label}s were found",
            code="RESOURCE_MISSING",
            resource_type=f"make_{label}",
            action=f"Confirm that the token can access at least one Make {label}, then rerun configure.",
            retry_safe=True,
        )
    if len(valid) == 1:
        return valid[0]

    output_fn(f"Multiple Make {label}s are available:")
    for index, item in enumerate(valid, start=1):
        output_fn(f"  {index}. {item['name']}")
    while True:
        raw = input_fn(f"Select the {label} to use [1-{len(valid)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(valid):
            return valid[int(raw) - 1]
        output_fn("Enter one of the listed numbers.")


def update_env(env_file: Path, updates: dict[str, str]) -> None:
    original = env_file.read_text(encoding="utf-8").splitlines()
    remaining = dict(updates)
    result: list[str] = []
    for line in original:
        stripped = line.strip()
        replaced = False
        for key in tuple(remaining):
            if stripped.startswith(f"{key}="):
                result.append(f'{key}="{remaining.pop(key)}"')
                replaced = True
                break
        if not replaced:
            result.append(line)
    if remaining:
        if result and result[-1].strip():
            result.append("")
        result.append("# Values discovered locally by python -m installer configure")
        for key in GENERATED_KEYS:
            if key in remaining:
                result.append(f'{key}="{remaining[key]}"')
    env_file.write_text("\n".join(result).rstrip() + "\n", encoding="utf-8")


def configure_environment(
    env_file: Path,
    *,
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
    client_factory: Callable[[str, str], MakeClient] | None = None,
) -> dict:
    zone, token, _notion_token = load_bootstrap(env_file)
    base_url = make_base_url(zone)
    client = client_factory(base_url, token) if client_factory else MakeClient(base_url, token)

    organizations = client.list_organizations()
    organization = _choose(organizations, "organization", input_fn, output_fn)
    organization_id = int(organization["id"])

    teams = [item for item in client.list_teams(organization_id) if item.get("organizationId") in (None, organization_id)]
    team = _choose(teams, "team", input_fn, output_fn)
    team_id = int(team["id"])

    update_env(
        env_file,
        {
            "MAKE_API_BASE_URL": base_url,
            "MAKE_ORGANIZATION_ID": str(organization_id),
            "MAKE_TEAM_ID": str(team_id),
        },
    )
    return {
        "status": "CONFIGURED",
        "environment_file": str(env_file),
        "make_zone": zone.casefold(),
        "organization": {"name": organization.get("name")},
        "team": {"name": team.get("name")},
        "written_keys": list(GENERATED_KEYS),
        "secrets_written": False,
    }
