from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from installer.blueprints import module_by_id, walk_modules


ROOT = Path(__file__).resolve().parents[2]
BLUEPRINT_PATH = ROOT / "setup" / "Make" / "blueprints" / "weft_archive_conversation.json"
CONFLICT_MESSAGE = "Conversation exists under a different project; request blocked without changes."


def route_flow(router: dict[str, Any], name: str) -> list[dict[str, Any]]:
    for route in router.get("routes", []):
        flow = route.get("flow", [])
        if not flow:
            continue
        route_filter = flow[0].get("filter") or {}
        if route_filter.get("name") == name:
            return flow
    raise AssertionError(f"router {router.get('id')} has no route named {name!r}")


def target_label(module: dict[str, Any]) -> str | None:
    restored = (((module.get("metadata") or {}).get("restore") or {}).get("expect") or {}).get("data_source") or {}
    rpc = restored.get("rpcSearch") if isinstance(restored, dict) else None
    return rpc.get("label") if isinstance(rpc, dict) else None


def field_values(module: dict[str, Any]) -> dict[str, Any]:
    labels: dict[str, str] = {}
    for item in (module.get("metadata") or {}).get("expect") or []:
        if isinstance(item, dict) and item.get("name") == "fields":
            labels = {
                str(spec["name"]): str(spec["label"])
                for spec in item.get("spec") or []
                if isinstance(spec, dict) and "name" in spec and "label" in spec
            }
            break
    fields = (module.get("mapper") or {}).get("fields") or {}
    return {labels.get(key, key): value for key, value in fields.items()}


class ArchiveBlueprintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.blueprint = json.loads(BLUEPRINT_PATH.read_text(encoding="utf-8-sig"))

    def module(self, module_id: int) -> dict[str, Any]:
        return module_by_id(self.blueprint, module_id)

    def test_validation_precedes_transcript_and_notion(self) -> None:
        self.assertEqual([module["id"] for module in self.blueprint["flow"]], [61, 340, 62, 106, 95])

        variables = {item["name"]: item["value"] for item in self.module(62)["mapper"]["variables"]}
        self.assertEqual(variables["conv_id"], "{{trim(61.conversation_id)}}")
        self.assertIn("length(62.conv_id)", self.module(106)["mapper"]["variables"][0]["value"])

        invalid = route_flow(self.module(95), "Invalid")
        self.assertEqual([module["module"] for module in invalid], ["scenario-service:ReturnData"])
        invalid_mapper = invalid[0]["mapper"]
        self.assertEqual(invalid_mapper["conversation_id"], '{{ifempty(62.conv_id; "missing")}}')
        self.assertEqual(invalid_mapper["error_type"], "validation_error")
        self.assertEqual(invalid_mapper["module"], "validation_router")

        valid = route_flow(self.module(95), "valid")
        self.assertEqual(valid[0]["module"], "builtin:BasicFeeder")
        self.assertTrue(any(module["module"].startswith("notion:") for _, module in walk_modules(valid)))
        self.assertFalse(any(module["module"].startswith("notion:") for module in self.blueprint["flow"][:-1]))

    def test_archive_writes_use_canonical_sources(self) -> None:
        writes = [
            module
            for _, module in walk_modules(self.blueprint)
            if module["module"] in {"notion:createDataSourceItem", "notion:updateADatabaseItem"}
            and target_label(module) == "Archive"
        ]
        self.assertEqual({module["id"] for module in writes}, {69, 71, 120, 123, 345})

        expected = {
            "Conversation ID": "{{62.conv_id}}",
            "Title": "{{62.title}}",
            "Start time": {"start": "{{62.started_at}}", "includeTime": True},
            "End time": {"start": "{{62.ended_at}}", "includeTime": True},
            "Message count": "{{62.msg_count}}",
            "Source": "{{62.source_norm}}",
            "Model origin": "{{62.platform_norm}}",
            "Extraction type": "{{62.extraction_type_norm}}",
            "Sentiment": "{{62.sentiment_norm}}",
            "Priority": "{{62.priority_norm}}",
            "Action items": "{{62.action_items_norm}}",
            "Key insights": "{{62.key_insights_norm}}",
            "Categories": "{{62.categories_norm}}",
            "Status": "{{62.status_norm}}",
            "Payload JSON": "{{substring(66.payload_raw_for_storage; 0; 1900)}}",
        }
        for module in writes:
            with self.subTest(module=module["id"]):
                fields = field_values(module)
                for label, value in expected.items():
                    self.assertEqual(fields[label], value)
                self.assertEqual(fields["Summary"], "{{61.summary}}")
                self.assertEqual(fields["Full content"], "{{substring(64.text; 0; 1900)}}")

        self.assertEqual(field_values(self.module(71))["Project"], "{{76.Project_id}}")
        self.assertEqual(field_values(self.module(120))["Project"], "{{117.Project_id}}")
        self.assertEqual(field_values(self.module(345))["Project"], "{{344.Project_id}}")
        self.assertNotIn("Project", field_values(self.module(69)))
        self.assertNotIn("Project", field_values(self.module(123)))
        self.assertEqual(field_values(self.module(71))["Project key"], "{{62.project_key}}")
        self.assertEqual(field_values(self.module(120))["Project key"], "{{62.project_key}}")

    def test_success_and_conflict_outputs_use_canonical_identity(self) -> None:
        outputs = [
            module
            for _, module in walk_modules(self.blueprint)
            if module["module"] == "scenario-service:ReturnData"
            and (module.get("mapper") or {}).get("status") in {"success", "blocked"}
        ]
        self.assertEqual({module["id"] for module in outputs}, {70, 72, 122, 125, 251, 269, 347})
        for module in outputs:
            mapper = module["mapper"]
            with self.subTest(module=module["id"]):
                self.assertEqual(mapper["conversation_id"], "{{62.conv_id}}")
                self.assertNotIn("properties_value", mapper["conversation_id"])

    def test_project_first_route_two_and_route_seven_guards(self) -> None:
        continuation = self.module(331)["routes"][1]["flow"]
        self.assertEqual([module["id"] for module in continuation], [339, 322, 73, 110])

        missing_project = route_flow(self.module(110), "Project not found")
        self.assertEqual([module["id"] for module in missing_project], [67, 68])
        self.assertEqual(self.module(67)["mapper"]["filter"][0][0]["b"], "{{62.conv_id}}")

        archive_missing = route_flow(self.module(68), "Page ID does not exits")
        self.assertEqual([module["id"] for module in archive_missing], [74, 76, 71, 93, 72])
        self.assertEqual(
            [module["module"] for module in archive_missing],
            [
                "notion:createDataSourceItem",
                "util:SetVariable2",
                "notion:createDataSourceItem",
                "notion:appendAPageContent",
                "scenario-service:ReturnData",
            ],
        )

        archive_found = route_flow(self.module(68), "Page ID exists")
        self.assertEqual([module["id"] for module in archive_found], [237])
        conflict = route_flow(self.module(237), "conflict")
        self.assertEqual([module["module"] for module in conflict], ["scenario-service:ReturnData"])
        self.assertEqual(conflict[0]["mapper"]["message"], CONFLICT_MESSAGE)
        self.assertEqual(conflict[0]["mapper"]["record_id"], "{{67.id}}")
        self.assertEqual(conflict[0]["mapper"]["notion_url"], "{{67.url}}")

    def test_route_six_repairs_relation_without_duplicate_archive(self) -> None:
        repair = route_flow(self.module(237), "Archive has no linked Project")
        self.assertEqual([module["id"] for module in repair], [343, 344, 345, 346, 347])
        self.assertEqual(repair[0]["module"], "notion:createDataSourceItem")
        self.assertEqual(target_label(repair[0]), "Projects")
        self.assertEqual(repair[2]["module"], "notion:updateADatabaseItem")
        self.assertEqual(repair[2]["mapper"]["page"], "{{67.id}}")
        self.assertEqual(field_values(repair[2])["Project"], "{{344.Project_id}}")
        self.assertFalse(any(module["module"] == "notion:createDataSourceItem" and target_label(module) == "Archive" for module in repair))
        self.assertEqual(repair[-1]["mapper"]["conversation_id"], "{{62.conv_id}}")

    def test_routes_three_four_and_five_remain_separate(self) -> None:
        project_found = route_flow(self.module(110), "Project found")
        self.assertEqual([module["id"] for module in project_found], [117, 118, 119])

        archive_missing = route_flow(self.module(119), "Page ID does not exist")
        self.assertEqual([module["id"] for module in archive_missing], [120, 121, 122])
        self.assertEqual(field_values(archive_missing[0])["Project"], "{{117.Project_id}}")

        archive_found = route_flow(self.module(119), "Page ID exists")
        self.assertEqual([module["id"] for module in archive_found], [239])
        match = route_flow(self.module(239), "Match - no conflict")
        self.assertEqual([module["id"] for module in match], [123, 124, 125])
        self.assertEqual(match[0]["mapper"]["page"], "{{118.id}}")
        self.assertNotIn("Project", field_values(match[0]))

        conflict = route_flow(self.module(239), "conflict")
        self.assertEqual([module["module"] for module in conflict], ["scenario-service:ReturnData"])
        mapper = conflict[0]["mapper"]
        self.assertEqual(mapper["message"], CONFLICT_MESSAGE)
        self.assertEqual(mapper["record_id"], "{{118.id}}")
        self.assertEqual(mapper["notion_url"], "{{118.url}}")
        self.assertEqual(mapper["conversation_id"], "{{62.conv_id}}")

    def test_legacy_conflict_mutations_are_absent(self) -> None:
        module_ids = {module["id"] for _, module in walk_modules(self.blueprint)}
        removed = {
            240, 268, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301,
            303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313,
        }
        self.assertTrue(removed.isdisjoint(module_ids))
        serialized = json.dumps(self.blueprint, ensure_ascii=False)
        self.assertNotIn("project fields frozen", serialized)
        self.assertNotIn("properties_value.Conversation_ID", serialized)


class RepositoryEnvironmentTests(unittest.TestCase):
    def test_env_is_ignored_and_example_is_empty(self) -> None:
        ignore_lines = {
            line.strip()
            for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        }
        self.assertIn(".env", ignore_lines)
        self.assertIn(".env.*", ignore_lines)
        self.assertIn("!.env.example", ignore_lines)

        for line in (ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                self.assertTrue(stripped.endswith("="), f"populated .env.example assignment: {stripped.split('=', 1)[0]}")


if __name__ == "__main__":
    unittest.main()
