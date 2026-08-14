from __future__ import annotations

import copy
import unittest
from pathlib import Path
from typing import Any

from installer.blueprints import (
    data_structure_contracts,
    load_manifest,
    load_registry,
    module_by_id,
    rebind_blueprint,
    source_connection_map,
    source_data_structure_map,
    source_notion_map,
    source_property_maps,
    source_scenario_map,
    validate_candidate,
)
from installer.tests.test_installer import target_notion_resources


ROOT = Path(__file__).resolve().parents[2]


class CandidateValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_manifest(ROOT)
        cls.registry = load_registry(ROOT, cls.manifest)
        contracts = data_structure_contracts(cls.manifest)
        cls.source_connections = source_connection_map(cls.registry)
        cls.source_structures = source_data_structure_map(cls.registry, contracts)
        cls.source_notion = source_notion_map(cls.registry, cls.manifest)
        cls.source_properties = source_property_maps(cls.registry, cls.source_notion, cls.manifest)
        cls.source_scenarios = source_scenario_map(cls.registry)
        cls.target_connections = {"notion": 701, "ai_provider": 702}
        cls.target_structures = {
            "archive_messages": 801,
            "search_archive_response": 802,
            "get_context_response": 803,
            "daily_log_content": 804,
        }
        cls.notion_resources = target_notion_resources()
        cls.target_scenarios = {
            key: 901 + index for index, key in enumerate(cls.registry)
        }

    def rebind(
        self,
        scenario_key: str,
        canonical: dict[str, Any],
        *,
        source_connections: dict[str, str] | None = None,
        source_structures: dict[str, str] | None = None,
        source_notion: dict[str, str] | None = None,
        source_properties: dict[str, dict[str, str]] | None = None,
        source_scenarios: dict[str, str] | None = None,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        return rebind_blueprint(
            scenario_key,
            canonical,
            source_connections=source_connections or self.source_connections,
            target_connections=self.target_connections,
            source_structures=source_structures or self.source_structures,
            target_structures=self.target_structures,
            source_notion=source_notion or self.source_notion,
            notion_resources=self.notion_resources,
            source_properties=source_properties or self.source_properties,
            source_scenarios=source_scenarios or self.source_scenarios,
            target_scenarios=self.target_scenarios,
            module_overrides=self.manifest.get("module_semantic_overrides", {}),
        )

    def validate(
        self,
        scenario_key: str,
        canonical: dict[str, Any],
        candidate: dict[str, Any],
        mutations: list[dict[str, Any]],
        unresolved: list[dict[str, Any]],
        *,
        source_structures: dict[str, str] | None = None,
        source_notion: dict[str, str] | None = None,
        source_scenarios: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        return validate_candidate(
            scenario_key,
            canonical,
            candidate,
            mutations,
            unresolved,
            source_structures=source_structures or self.source_structures,
            source_notion=source_notion or self.source_notion,
            source_scenarios=source_scenarios or self.source_scenarios,
            target_connections=self.target_connections,
            target_structures=self.target_structures,
            notion_resources=self.notion_resources,
            target_scenarios=self.target_scenarios,
        )

    def already_bound(self, scenario_key: str) -> tuple[
        dict[str, Any],
        dict[str, Any],
        list[dict[str, Any]],
        list[dict[str, Any]],
        dict[str, str],
        dict[str, str],
        dict[str, dict[str, str]],
        dict[str, str],
    ]:
        canonical = self.registry[scenario_key]["blueprint"]
        bound, first_mutations, first_unresolved = self.rebind(scenario_key, canonical)
        self.assertTrue(first_mutations)
        self.assertEqual(first_unresolved, [])

        bound_connections = {str(value): key for key, value in self.target_connections.items()}
        bound_structures = {str(value): key for key, value in self.target_structures.items()}
        bound_notion = {
            str(resource["data_source_id"]): semantic
            for semantic, resource in self.notion_resources.items()
        }
        bound_properties = {
            semantic: {
                str(spec["id"]): label
                for label, spec in resource["properties"].items()
            }
            for semantic, resource in self.notion_resources.items()
        }
        bound_scenarios = {
            f"SCN_{value}": key for key, value in self.target_scenarios.items()
        }
        candidate, mutations, unresolved = self.rebind(
            scenario_key,
            bound,
            source_connections=bound_connections,
            source_structures=bound_structures,
            source_notion=bound_notion,
            source_properties=bound_properties,
            source_scenarios=bound_scenarios,
        )
        return (
            bound,
            candidate,
            mutations,
            unresolved,
            bound_structures,
            bound_notion,
            bound_properties,
            bound_scenarios,
        )

    def test_create_daily_log_with_real_mutations_passes_as_rebound(self) -> None:
        canonical = self.registry["create_daily_log"]["blueprint"]
        candidate, mutations, unresolved = self.rebind("create_daily_log", canonical)
        result = self.validate("create_daily_log", canonical, candidate, mutations, unresolved)
        self.assertTrue(mutations)
        self.assertTrue(result["passed"])
        self.assertEqual(result["candidate_mode"], "rebound")

    def test_create_daily_log_with_correct_zero_mutation_candidate_passes(self) -> None:
        (
            canonical,
            candidate,
            mutations,
            unresolved,
            source_structures,
            source_notion,
            _,
            source_scenarios,
        ) = self.already_bound("create_daily_log")
        result = self.validate(
            "create_daily_log",
            canonical,
            candidate,
            mutations,
            unresolved,
            source_structures=source_structures,
            source_notion=source_notion,
            source_scenarios=source_scenarios,
        )
        self.assertEqual(mutations, [])
        self.assertEqual(unresolved, [])
        self.assertTrue(result["passed"])
        self.assertEqual(result["candidate_mode"], "no_op")
        self.assertNotIn("mutation_manifest_nonempty_when_required", result["checks"])

    def test_another_correct_zero_mutation_scenario_passes(self) -> None:
        (
            canonical,
            candidate,
            mutations,
            unresolved,
            source_structures,
            source_notion,
            _,
            source_scenarios,
        ) = self.already_bound("search_archive")
        result = self.validate(
            "search_archive",
            canonical,
            candidate,
            mutations,
            unresolved,
            source_structures=source_structures,
            source_notion=source_notion,
            source_scenarios=source_scenarios,
        )
        self.assertEqual(mutations, [])
        self.assertTrue(result["passed"])
        self.assertEqual(result["candidate_mode"], "no_op")

    def test_zero_mutations_with_unresolved_binding_fails(self) -> None:
        canonical = self.registry["create_daily_log"]["blueprint"]
        result = self.validate(
            "create_daily_log",
            canonical,
            copy.deepcopy(canonical),
            [],
            [{"category": "connection", "path": "$.flow[0].parameters.__IMTCONN__"}],
        )
        self.assertFalse(result["passed"])
        self.assertIn("no_unresolved_bindings", result["failed_checks"])
        self.assertEqual(result["candidate_mode"], "no_op")

    def synthetic_candidate(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        canonical = {
            "name": "synthetic",
            "flow": [
                {
                    "id": 1,
                    "module": "notion:searchObjects1",
                    "parameters": {"__IMTCONN__": 701},
                    "mapper": {"data_source": "archive-target"},
                    "metadata": {
                        "restore": {
                            "expect": {
                                "data_source": {
                                    "rpcSearch": {"value": "archive-target", "label": "Archive"}
                                }
                            }
                        }
                    },
                },
                {
                    "id": 2,
                    "module": "json:ParseJSON",
                    "parameters": {"type": 801},
                    "mapper": {},
                    "metadata": {"restore": {"parameters": {"type": {"label": "Archive"}}}},
                },
                {
                    "id": 3,
                    "module": "scenario-service:CallSubscenario",
                    "parameters": {"scenario": "SCN_901"},
                    "mapper": {},
                    "metadata": {},
                },
            ],
            "io": {"input_spec": [], "output_spec": []},
        }
        resources = {
            "Archive": {"data_source_id": "archive-target", "properties": {}},
            "Projects": {"data_source_id": "projects-target", "properties": {}},
        }
        arguments = {
            "source_structures": {"801": "archive_messages"},
            "source_notion": {"archive-target": "Archive"},
            "source_scenarios": {"SCN_901": "notion_text_formatter"},
            "target_connections": {"notion": 701, "ai_provider": 702},
            "target_structures": {"archive_messages": 801, "search_archive_response": 802},
            "notion_resources": resources,
            "target_scenarios": {"notion_text_formatter": 901, "search_archive": 902},
        }
        return canonical, copy.deepcopy(canonical), arguments

    def validate_synthetic(
        self,
        canonical: dict[str, Any],
        candidate: dict[str, Any],
        arguments: dict[str, Any],
        unresolved: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return validate_candidate(
            "synthetic",
            canonical,
            candidate,
            [],
            unresolved or [],
            **arguments,
        )

    def test_zero_mutations_with_wrong_connection_or_notion_source_fails(self) -> None:
        canonical, candidate, arguments = self.synthetic_candidate()
        candidate["flow"][0]["parameters"]["__IMTCONN__"] = 702
        result = self.validate_synthetic(canonical, candidate, arguments)
        self.assertFalse(result["checks"]["connections_resolved"])
        self.assertFalse(result["passed"])

        canonical, candidate, arguments = self.synthetic_candidate()
        candidate["flow"][0]["mapper"]["data_source"] = "projects-target"
        result = self.validate_synthetic(canonical, candidate, arguments)
        self.assertFalse(result["checks"]["notion_sources_resolved"])
        self.assertFalse(result["passed"])

    def test_wrong_data_structure_or_scenario_dependency_fails(self) -> None:
        canonical, candidate, arguments = self.synthetic_candidate()
        candidate["flow"][1]["parameters"]["type"] = 802
        result = self.validate_synthetic(canonical, candidate, arguments)
        self.assertFalse(result["checks"]["data_structures_resolved"])
        self.assertFalse(result["passed"])

        canonical, candidate, arguments = self.synthetic_candidate()
        candidate["flow"][2]["parameters"]["scenario"] = "SCN_902"
        result = self.validate_synthetic(canonical, candidate, arguments)
        self.assertFalse(result["checks"]["scenario_dependencies_resolved"])
        self.assertFalse(result["passed"])

    def test_topology_or_public_interface_mismatch_fails(self) -> None:
        canonical, candidate, arguments = self.synthetic_candidate()
        candidate["flow"].pop()
        result = self.validate_synthetic(canonical, candidate, arguments)
        self.assertFalse(result["checks"]["topology_unchanged"])
        self.assertFalse(result["passed"])

        canonical, candidate, arguments = self.synthetic_candidate()
        candidate["io"]["output_spec"].append({"name": "unexpected", "type": "text"})
        result = self.validate_synthetic(canonical, candidate, arguments)
        self.assertFalse(result["checks"]["public_interface_unchanged"])
        self.assertFalse(result["passed"])

    def test_create_daily_log_specific_checks_remain_fail_closed(self) -> None:
        canonical = self.registry["create_daily_log"]["blueprint"]
        candidate, mutations, unresolved = self.rebind("create_daily_log", canonical)
        module_by_id(candidate, 14)["mapper"]["filter"] = []
        result = self.validate("create_daily_log", canonical, candidate, mutations, unresolved)
        self.assertFalse(result["checks"]["daily_log_filter_preserved"])
        self.assertFalse(result["passed"])

        candidate, mutations, unresolved = self.rebind("create_daily_log", canonical)
        module_by_id(candidate, 43)["parameters"]["model"] = "large"
        result = self.validate("create_daily_log", canonical, candidate, mutations, unresolved)
        self.assertFalse(result["checks"]["ai_provider_and_model_preserved"])
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
