"""Configuration loading and validation for the public installer."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

from .errors import InstallerError

SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,59}$")


@dataclass(frozen=True)
class Config:
    repo_root: Path
    make_api_base_url: str
    make_token: str
    make_team_id: int
    make_organization_id: int
    notion_token: str
    installation_name: str
    state_file: Path
    notion_connection_id: int | None = None
    ai_connection_id: int | None = None

    @property
    def secrets(self) -> tuple[str, ...]:
        return tuple(value for value in (self.make_token, self.notion_token) if value)


def _optional_id(name: str, value: str) -> int | None:
    if not value:
        return None
    if not value.isdigit() or int(value) <= 0:
        raise InstallerError(f"{name} must be a positive integer when supplied", code="INVALID_CONFIGURATION", config_key=name)
    return int(value)


def _api_root(raw: str) -> str:
    parsed = urlparse(raw)
    if parsed.scheme != "https" or not parsed.hostname:
        raise InstallerError("MAKE_API_BASE_URL must be an HTTPS URL", code="INVALID_CONFIGURATION", config_key="MAKE_API_BASE_URL")
    host = parsed.hostname.casefold()
    if host != "make.com" and not host.endswith(".make.com"):
        raise InstallerError("MAKE_API_BASE_URL must use an official make.com host", code="INVALID_CONFIGURATION", config_key="MAKE_API_BASE_URL")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise InstallerError("MAKE_API_BASE_URL contains unsupported URL components", code="INVALID_CONFIGURATION", config_key="MAKE_API_BASE_URL")
    return raw.rstrip("/")


def load_config(repo_root: Path, env_file: Path | None = None, environ: dict[str, str] | None = None) -> Config:
    if environ is None:
        load_dotenv(env_file or repo_root / ".env", override=True)
        values = os.environ
    else:
        values = environ

    required = ("MAKE_API_BASE_URL", "MAKE_API_TOKEN", "MAKE_TEAM_ID", "MAKE_ORGANIZATION_ID", "NOTION_INSPECT_TOKEN")
    raw = {name: str(values.get(name, "")).strip() for name in required}
    missing = [name for name, value in raw.items() if not value]
    if missing:
        raise InstallerError(
            f"Missing required configuration: {', '.join(missing)}",
            code="MISSING_CONFIGURATION",
            action="Run python -m installer configure before preflight.",
            retry_safe=True,
        )
    for name in ("MAKE_TEAM_ID", "MAKE_ORGANIZATION_ID"):
        if not raw[name].isdigit() or int(raw[name]) <= 0:
            raise InstallerError(f"{name} must be a positive integer", code="INVALID_CONFIGURATION", config_key=name)

    installation_name = str(values.get("WEFT_INSTALLATION_NAME", "")).strip() or "Weft"
    if not SAFE_NAME.fullmatch(installation_name):
        raise InstallerError(
            "WEFT_INSTALLATION_NAME must be 1-60 characters using letters, numbers, spaces, dots, underscores, or hyphens",
            code="INVALID_CONFIGURATION",
            config_key="WEFT_INSTALLATION_NAME",
        )

    configured_state = str(values.get("WEFT_STATE_FILE", "")).strip()
    state_file = Path(configured_state) if configured_state else repo_root / ".weft-installer" / "installation-state.json"
    if not state_file.is_absolute():
        state_file = (repo_root / state_file).resolve()
    private_state_root = (repo_root / ".weft-installer").resolve()
    try:
        state_file.relative_to(private_state_root)
    except ValueError:
        raise InstallerError(
            "WEFT_STATE_FILE must remain under the ignored .weft-installer directory",
            code="INVALID_CONFIGURATION",
            config_key="WEFT_STATE_FILE",
            action="Choose a path under .weft-installer so target IDs cannot enter publication files.",
            retry_safe=True,
        ) from None

    return Config(
        repo_root=repo_root.resolve(),
        make_api_base_url=_api_root(raw["MAKE_API_BASE_URL"]),
        make_token=raw["MAKE_API_TOKEN"],
        make_team_id=int(raw["MAKE_TEAM_ID"]),
        make_organization_id=int(raw["MAKE_ORGANIZATION_ID"]),
        notion_token=raw["NOTION_INSPECT_TOKEN"],
        installation_name=installation_name,
        state_file=state_file,
        notion_connection_id=_optional_id("WEFT_NOTION_CONNECTION_ID", str(values.get("WEFT_NOTION_CONNECTION_ID", "")).strip()),
        ai_connection_id=_optional_id("WEFT_AI_CONNECTION_ID", str(values.get("WEFT_AI_CONNECTION_ID", "")).strip()),
    )
