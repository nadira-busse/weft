#!/usr/bin/env python3
"""Audit tracked and unignored publication files for repository hygiene."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_ENV_KEYS = {
    "NOTION_INSPECT_TOKEN",
    "MAKE_API_TOKEN",
    "MAKE_ZONE",
    "MAKE_API_BASE_URL",
    "MAKE_ORGANIZATION_ID",
    "MAKE_TEAM_ID",
    "WEFT_NOTION_CONNECTION_ID",
    "WEFT_AI_CONNECTION_ID",
    "WEFT_INSTALLATION_NAME",
    "WEFT_STATE_FILE",
}
SECRET_PATTERN = re.compile(
    r"AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|"
    r"ntn_[A-Za-z0-9]{20,}|Bearer [A-Za-z0-9._-]{12,}|Token [A-Za-z0-9._-]{12,}"
)
CREDENTIAL_ASSIGNMENT = re.compile(
    r"(api[_-]?key|api[_-]?token|access[_-]?token|secret|authorization)"
    r"\s*[:=]\s*[\"']?[A-Za-z0-9._-]{12,}",
    re.I,
)
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
MACHINE_PATH = re.compile(r"[A-Z]:\\Users\\[^\s`)]*|/Users/[^\s`)]*|/home/[^\s`)]*")


def publication_files() -> list[Path]:
    raw = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    )
    return [
        ROOT / relative
        for relative in raw.decode("utf-8", "surrogateescape").split("\0")
        if relative and (ROOT / relative).is_file()
    ]


def audit() -> tuple[dict[str, object], bool]:
    files = publication_files()
    report: dict[str, object] = {
        "publication_files": len(files),
        "json_parsed": 0,
        "json_errors": [],
        "zero_byte": [],
        "placeholders": [],
        "obsolete_schema_paths": [],
        "nonlocal_proof_refs": [],
        "machine_paths": [],
        "secret_tokens": [],
        "credential_assignments": [],
        "email_addresses": [],
        "private_installer_dependencies": [],
        "env_example_errors": [],
    }

    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix.casefold() == ".json":
            report["json_parsed"] = int(report["json_parsed"]) + 1
            try:
                json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError) as exc:
                report["json_errors"].append(f"{relative}: {exc}")
        if path.stat().st_size == 0:
            report["zero_byte"].append(relative)
        try:
            text = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError):
            continue
        is_audit_source = relative == "scripts/audit_publication.py"
        for line_number, line in enumerate(text.splitlines(), 1):
            location = f"{relative}:{line_number}"
            # The scanner source necessarily contains the signatures it detects.
            if not is_audit_source and re.search(r"\b(TODO|FIXME|TBD)\b", line, re.I):
                report["placeholders"].append(location)
            if not is_audit_source and re.search(r"schemas/(archive|search|context)/", line):
                report["obsolete_schema_paths"].append(location)
            if not is_audit_source and re.search(r"\]\((?:\.\./)*proof/", line):
                report["nonlocal_proof_refs"].append(location)
            if not is_audit_source and MACHINE_PATH.search(line):
                report["machine_paths"].append(location)
            if not is_audit_source and SECRET_PATTERN.search(line):
                report["secret_tokens"].append(location)
            if not is_audit_source and CREDENTIAL_ASSIGNMENT.search(line):
                report["credential_assignments"].append(location)
            if not is_audit_source and EMAIL.search(line):
                report["email_addresses"].append(location)
            if relative.startswith("installer/") and not relative.startswith("installer/tests/"):
                if ".agent-private" in line or ".private" in line:
                    report["private_installer_dependencies"].append(location)

    env_path = ROOT / ".env.example"
    env_values: dict[str, str] = {}
    for line_number, line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            report["env_example_errors"].append(f".env.example:{line_number}: malformed assignment")
            continue
        key, value = stripped.split("=", 1)
        env_values[key] = value
        if value:
            report["env_example_errors"].append(f".env.example:{line_number}: value must be empty")
    missing = sorted(EXPECTED_ENV_KEYS - set(env_values))
    extra = sorted(set(env_values) - EXPECTED_ENV_KEYS)
    if missing:
        report["env_example_errors"].append(f"missing keys: {missing}")
    if extra:
        report["env_example_errors"].append(f"unexpected keys: {extra}")

    failed = any(value for value in report.values() if isinstance(value, list))
    return report, failed


def main() -> int:
    report, failed = audit()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
