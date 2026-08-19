from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from installer.blueprints import (
    _metadata_field_specs,
    _module_semantic,
    file_hash,
    load_manifest,
    load_registry,
    source_notion_map,
    source_scenario_map,
    walk_modules,
)
from installer.config import Config, load_config
from installer.engine import Installer, sanitize_report
from installer.cli import compact_terminal_report
from installer.errors import InstallerError


ROOT = Path(__file__).resolve().parents[2]


def target_notion_resources() -> dict[str, Any]:
    manifest = load_manifest(ROOT)
    registry = load_registry(ROOT, manifest)
    source_map = source_notion_map(registry, manifest)
    resources: dict[str, Any] = {
        item["key"]: {
            "title": item["title"],
            "database_id": f"target-db-{index}",
            "data_source_id": f"target-data-source-{index}",
            "properties": {},
        }
        for index, item in enumerate(manifest["notion_resources"], 1)
    }
    overrides = manifest["module_semantic_overrides"]
    for scenario_key, record in registry.items():
        for _, module in walk_modules(record["blueprint"]):
            if not str(module.get("module", "")).startswith("notion:"):
                continue
            semantic = _module_semantic(module, source_map, overrides.get(scenario_key, {}))
            if semantic not in resources:
                continue
            for spec in _metadata_field_specs(module).values():
                label = spec.get("label")
                if not isinstance(label, str) or not label:
                    continue
                metadata = spec.get("metadata") if isinstance(spec.get("metadata"), dict) else {}
                notion_type = metadata.get("type")
                if not notion_type:
                    notion_type = {"text": "rich_text", "number": "number", "boolean": "checkbox", "collection": "date"}.get(spec.get("type"), spec.get("type"))
                resources[semantic]["properties"].setdefault(
                    label,
                    {"id": f"target-property-{semantic.casefold().replace(' ', '-')}-{len(resources[semantic]['properties']) + 1}", "type": notion_type, "configuration": {}},
                )
    return resources


class FakeNotion:
    def __init__(self, resources: dict[str, Any] | None = None) -> None:
        self.resources = resources or target_notion_resources()
        self.mutation_count = 0

    def discover_resources(self, requested: list[dict[str, str]]) -> dict[str, Any]:
        missing = [item["key"] for item in requested if item["key"] not in self.resources]
        if missing:
            raise InstallerError(
                f"Missing Notion resources: {missing}",
                code="NOTION_RESOURCE_MISSING",
                resource_type="notion_data_source",
                action="Share the missing database.",
            )
        return copy.deepcopy(self.resources)


class FakeMake:
    def __init__(self) -> None:
        self.mutation_count = 0
        self.request_log: list[dict[str, Any]] = []
        self.connections = [
            {"id": 701, "name": "Weft Notion", "accountName": "notion3", "accountType": "basic", "teamId": 11, "organizationId": 22, "scoped": True},
            {"id": 702, "name": "Weft AI", "accountName": "ai-provider", "accountType": "basic", "teamId": 11, "organizationId": 22, "scoped": True},
        ]
        self.structures: dict[int, dict[str, Any]] = {}
        self.scenarios: dict[int, dict[str, Any]] = {}
        self.next_structure = 800
        self.next_scenario = 900

    def request(self, method: str, path: str, *, write: bool = False, body: dict[str, Any] | None = None) -> dict[str, Any]:
        self.request_log.append({"method": method, "path": path, "mutation": method != "GET"})
        if path == "/users/me/current-authorization":
            scopes = ["scenarios:read", "scenarios:write", "connections:read", "udts:read", "udts:write", "teams:read", "organizations:read"]
            return {"scopes": scopes}
        if path == "/teams/11":
            return {"team": {"id": 11, "name": "Test team", "organizationId": 22}}
        if path == "/organizations/22":
            return {"organization": {"id": 22, "name": "Test organization", "zone": "eu2"}}
        raise AssertionError(f"Unexpected request {method} {path}")

    @staticmethod
    def unwrap_record(payload: Any, key: str) -> dict[str, Any]:
        return payload.get(key, payload) if isinstance(payload, dict) else {}

    def list_scenarios(self, team_id: int) -> list[dict[str, Any]]:
        return [copy.deepcopy(item["detail"]) for item in self.scenarios.values()]

    def list_connections(self, team_id: int) -> list[dict[str, Any]]:
        return copy.deepcopy(self.connections)

    def list_data_structures(self, team_id: int) -> list[dict[str, Any]]:
        return [copy.deepcopy(item) for item in self.structures.values()]

    def create_data_structure(self, body: dict[str, Any]) -> dict[str, Any]:
        self.mutation_count += 1
        self.next_structure += 1
        value = {"id": self.next_structure, **copy.deepcopy(body)}
        self.structures[self.next_structure] = value
        return copy.deepcopy(value)

    def get_data_structure(self, structure_id: int) -> dict[str, Any]:
        return copy.deepcopy(self.structures[structure_id])

    def create_scenario(self, body: dict[str, Any]) -> dict[str, Any]:
        self.mutation_count += 1
        self.next_scenario += 1
        blueprint = json.loads(body["blueprint"])
        detail = {"id": self.next_scenario, "name": blueprint["name"], "teamId": body["teamId"], "isActive": False}
        interface = copy.deepcopy(body.get("metadata", {}))
        self.scenarios[self.next_scenario] = {"detail": detail, "blueprint": blueprint, "interface": interface}
        return copy.deepcopy(detail)

    def get_scenario(self, scenario_id: int) -> dict[str, Any]:
        return copy.deepcopy(self.scenarios[scenario_id]["detail"])

    def get_scenario_blueprint(self, scenario_id: int) -> dict[str, Any]:
        return {"blueprint": json.dumps(self.scenarios[scenario_id]["blueprint"], separators=(",", ":"))}

    def get_scenario_interface(self, scenario_id: int) -> dict[str, Any]:
        return copy.deepcopy(self.scenarios[scenario_id]["interface"])

    def stop_scenario(self, scenario_id: int) -> None:
        self.mutation_count += 1
        self.scenarios[scenario_id]["detail"]["isActive"] = False


def config(state_file: Path) -> Config:
    return Config(
        repo_root=ROOT,
        make_api_base_url="https://eu2.make.com/api/v2",
        make_token="token-for-test",
        make_team_id=11,
        make_organization_id=22,
        notion_token="notion-token-for-test",
        installation_name="Weft Test",
        state_file=state_file,
    )


class InstallerTests(unittest.TestCase):
    def test_state_file_cannot_escape_ignored_directory(self) -> None:
        values = {
            "MAKE_API_BASE_URL": "https://eu2.make.com/api/v2",
            "MAKE_API_TOKEN": "token",
            "MAKE_TEAM_ID": "11",
            "MAKE_ORGANIZATION_ID": "22",
            "NOTION_INSPECT_TOKEN": "notion-token",
            "WEFT_STATE_FILE": "public-state.json",
        }
        with self.assertRaisesRegex(InstallerError, "ignored .weft-installer"):
            load_config(ROOT, environ=values)

    def test_missing_configuration_fails_before_clients(self) -> None:
        with self.assertRaises(InstallerError) as caught:
            load_config(ROOT, environ={})
        self.assertEqual(caught.exception.code, "MISSING_CONFIGURATION")
        self.assertTrue(caught.exception.retry_safe)

    def test_preflight_is_read_only_and_structural(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            make = FakeMake()
            notion = FakeNotion()
            engine = Installer(config(Path(directory) / "state.json"), make, notion)
            before = {key: file_hash(record["path"]) for key, record in engine.registry.items()}
            result = engine.preflight()
            after = {key: file_hash(record["path"]) for key, record in engine.registry.items()}
            self.assertEqual(result["status"], "PREFLIGHT_PASSED")
            self.assertEqual(make.mutation_count, 0)
            self.assertEqual(notion.mutation_count, 0)
            self.assertEqual(before, after)
            self.assertTrue(all(item["global_string_replacement_used"] is False for item in result["candidate_checks"].values()))

    def test_install_creates_four_structures_and_five_inactive_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_file = Path(directory) / "state.json"
            make = FakeMake()
            engine = Installer(config(state_file), make, FakeNotion())
            result = engine.install()
            self.assertEqual(result["status"], "LOCALLY_VERIFIED_CLEAN_INSTALL_PENDING")
            self.assertEqual(len(make.structures), 4)
            self.assertEqual(len(make.scenarios), 5)
            self.assertTrue(all(item["detail"]["isActive"] is False for item in make.scenarios.values()))
            formatter_id = result["scenarios"]["notion_text_formatter"]["id"]
            get_context = make.scenarios[result["scenarios"]["get_context"]["id"]]["blueprint"]
            serialized = json.dumps(get_context)
            self.assertIn(f"SCN_{formatter_id}", serialized)
            for source_reference in source_scenario_map(engine.registry):
                self.assertNotIn(source_reference, serialized)
            self.assertTrue((state_file.parent / "installation-report.sanitized.json").exists())
            self.assertEqual(len(list((state_file.parent / "candidates").glob("*.candidate.json"))), 5)
            self.assertEqual(len(list((state_file.parent / "candidates").glob("*.binding-manifest.json"))), 5)
            sanitized = json.loads((state_file.parent / "installation-report.sanitized.json").read_text(encoding="utf-8"))
            identifier_values: list[str] = []

            def collect_identifier_values(value: Any) -> None:
                if isinstance(value, dict):
                    for key, item in value.items():
                        if key == "id" or key.endswith("_id"):
                            identifier_values.append(str(item))
                        collect_identifier_values(item)
                elif isinstance(value, list):
                    for item in value:
                        collect_identifier_values(item)

            collect_identifier_values(sanitized)

            self.assertNotIn(str(formatter_id), identifier_values)

    def test_rerun_uses_state_without_duplicate_creation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state_file = Path(directory) / "state.json"
            make = FakeMake()
            notion = FakeNotion()
            Installer(config(state_file), make, notion).install()
            mutations = make.mutation_count
            result = Installer(config(state_file), make, notion).install()
            self.assertEqual(make.mutation_count, mutations)
            self.assertEqual(len(make.structures), 4)
            self.assertEqual(len(make.scenarios), 5)
            self.assertTrue(all(item["status"] == "REUSED_AND_VERIFIED" for item in result["scenarios"].values()))

    def test_ambiguous_ai_connection_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            make = FakeMake()
            duplicate = copy.deepcopy(make.connections[1])
            duplicate["id"] = 703
            duplicate["name"] = "Second AI"
            make.connections.append(duplicate)
            with self.assertRaises(InstallerError) as caught:
                Installer(config(Path(directory) / "state.json"), make, FakeNotion()).preflight()
            self.assertEqual(caught.exception.code, "CONNECTION_AMBIGUOUS")
            self.assertEqual(len(caught.exception.candidates), 2)
            self.assertEqual(make.mutation_count, 0)

    def test_missing_ai_connection_reports_manual_ui_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            make = FakeMake()
            make.connections = make.connections[:1]
            with self.assertRaises(InstallerError) as caught:
                Installer(config(Path(directory) / "state.json"), make, FakeNotion()).preflight()
            self.assertEqual(caught.exception.code, "MANUAL_UI_CONNECTION_REQUIRED")
            self.assertIn("open an AI module", caught.exception.action or "")

    def test_ambiguous_installer_named_data_structure_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            make = FakeMake()
            contract = load_manifest(ROOT)["data_structures"][0]
            for structure_id in (801, 802):
                make.structures[structure_id] = {
                    "id": structure_id,
                    "teamId": 11,
                    "name": contract["name"],
                    "strict": False,
                    "spec": copy.deepcopy(contract["spec"]),
                }
            with self.assertRaises(InstallerError) as caught:
                Installer(config(Path(directory) / "state.json"), make, FakeNotion()).preflight()
            self.assertEqual(caught.exception.code, "DATA_STRUCTURE_AMBIGUOUS")
            self.assertEqual(make.mutation_count, 0)

    def test_missing_notion_resource_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            resources = target_notion_resources()
            resources.pop("Archive")
            with self.assertRaises(InstallerError) as caught:
                Installer(config(Path(directory) / "state.json"), FakeMake(), FakeNotion(resources)).preflight()
            self.assertEqual(caught.exception.code, "NOTION_RESOURCE_MISSING")

    def test_unowned_scenario_name_is_not_adopted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            make = FakeMake()
            make.scenarios[999] = {
                "detail": {"id": 999, "name": "Weft Test - archive_conversation", "teamId": 11, "isActive": False},
                "blueprint": {},
                "interface": {},
            }
            with self.assertRaises(InstallerError) as caught:
                Installer(config(Path(directory) / "state.json"), make, FakeNotion()).preflight()
            self.assertEqual(caught.exception.code, "UNOWNED_SCENARIO_NAME")
            self.assertFalse(caught.exception.retry_safe)

    def test_sanitized_report_redacts_nested_ids(self) -> None:
        value = {"team_id": 11, "items": [{"id": 22, "name": "safe"}], "count": 3}
        sanitized = sanitize_report(value)
        self.assertEqual(sanitized["team_id"], "<redacted>")
        self.assertEqual(sanitized["items"][0]["id"], "<redacted>")
        self.assertEqual(sanitized["count"], 3)

    def test_public_docs_use_real_entrypoint_and_no_private_runtime_dependency(self) -> None:
        setup = (ROOT / "setup" / "make-provisioning.md").read_text(encoding="utf-8")
        self.assertIn("python -m installer preflight", setup)
        self.assertIn("python -m installer install", setup)
        self.assertNotIn("Create an empty scenario", setup)
        self.assertNotIn("Replace every Notion connection", setup)
        public_source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "installer").rglob("*.py")
            if "tests" not in path.parts
        )
        self.assertNotIn(".agent-private", public_source)



    def test_preflight_terminal_report_is_compact(self) -> None:
        report = {
            "status": "PREFLIGHT_PASSED",
            "target": {"organization": {"name": "Org"}, "team": {"name": "Team"}},
            "notion_resources": {"Archive": {}, "Projects": {}, "Daily Log": {}, "Error Logs": {}},
            "data_structure_plans": {"a": {}, "b": {}, "c": {}, "d": {}},
            "scenario_plans": {"one": {"action": "create"}, "two": {"action": "reuse_exact"}},
            "performed_make_mutations": 0,
            "performed_notion_mutations": 0,
            "state_found": False,
        }
        compact = compact_terminal_report("preflight", report)
        self.assertEqual(compact["notion_databases_found"], 4)
        self.assertEqual(compact["data_structures_planned"], 4)
        self.assertEqual(compact["scenarios_planned"], 2)
        self.assertNotIn("notion_resources", compact)
        self.assertEqual(compact["performed_make_mutations"], 0)

if __name__ == "__main__":
    unittest.main()
