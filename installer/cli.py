"""Command-line entrypoint for the public installer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .clients import MakeClient, NotionClient
from .config import load_config
from .configure import configure_environment
from .engine import Installer, sanitize_report
from .errors import InstallerError


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Configure, provision, and statically verify Weft in Make.")
    result.add_argument("command", choices=("configure", "preflight", "install"), help="Local configuration, read-only preflight, or stateful installation.")
    result.add_argument("--env-file", type=Path, help="Environment file; defaults to .env at the repository root.")
    result.add_argument("--show-ids", action="store_true", help="Show target IDs in terminal JSON. Reports remain in the ignored state directory.")
    return result




def compact_terminal_report(command: str, report: dict) -> dict:
    """Return concise, user-facing output while full reports remain on disk."""
    if command != "preflight" or report.get("status") != "PREFLIGHT_PASSED":
        return report
    target = report.get("target", {})
    scenario_plans = report.get("scenario_plans", {})
    structure_plans = report.get("data_structure_plans", {})
    notion_resources = report.get("notion_resources", {})
    return {
        "status": report.get("status"),
        "organization": target.get("organization"),
        "team": target.get("team"),
        "notion_databases_found": len(notion_resources),
        "data_structures_planned": len(structure_plans),
        "scenarios_planned": len(scenario_plans),
        "scenario_actions": {name: plan.get("action") for name, plan in scenario_plans.items()},
        "performed_make_mutations": report.get("performed_make_mutations", 0),
        "performed_notion_mutations": report.get("performed_notion_mutations", 0),
        "state_found": report.get("state_found", False),
        "full_report": ".weft-installer/preflight-report.sanitized.json",
    }

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    arguments = parser().parse_args(argv)
    repo_root = Path(__file__).resolve().parents[1]
    env_file = (arguments.env_file or repo_root / ".env").resolve()
    installer: Installer | None = None
    try:
        if arguments.command == "configure":
            report = configure_environment(env_file)
        else:
            config = load_config(repo_root, env_file)
            make = MakeClient(config.make_api_base_url, config.make_token)
            notion = NotionClient(config.notion_token)
            installer = Installer(config, make, notion)
            if arguments.command == "preflight":
                report = installer.preflight()
                installer.write_preflight_report(report)
            else:
                report = installer.install()
        terminal_source = compact_terminal_report(arguments.command, report)
        terminal = terminal_source if arguments.show_ids else sanitize_report(terminal_source)
        print(json.dumps(terminal, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except InstallerError as exc:
        if installer is not None:
            try:
                installer.record_failure(exc)
            except InstallerError:
                pass
        print(json.dumps(exc.to_dict(), ensure_ascii=False, indent=2, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
