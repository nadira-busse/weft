"""Stateful, fail-closed provisioning engine for Weft."""

from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .blueprints import (
    data_structure_contracts,
    dependency_order,
    extract_readback_blueprint,
    file_hash,
    load_manifest,
    load_registry,
    make_create_body,
    rebind_blueprint,
    schemas_compatible,
    source_connection_map,
    source_data_structure_map,
    source_notion_map,
    source_property_maps,
    source_scenario_map,
    validate_candidate,
    verify_scenario_readback,
)
from .clients import AmbiguousMutationError, MakeClient, NotionClient
from .config import Config
from .errors import InstallerError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _scope_strings(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() in {"scope", "scopes"}:
                if isinstance(child, str):
                    found.update(part for part in child.replace(",", " ").split() if ":" in part)
                elif isinstance(child, list):
                    found.update(str(part) for part in child if isinstance(part, str))
            found.update(_scope_strings(child))
    elif isinstance(value, list):
        for child in value:
            found.update(_scope_strings(child))
    return found


def _has_scope(scopes: set[str], required: str) -> bool:
    family = required.split(":", 1)[0]
    return required in scopes or f"{family}:*" in scopes


def _safe_connection(record: dict[str, Any]) -> dict[str, Any]:
    return {key: record.get(key) for key in ("id", "name", "accountName", "accountType", "teamId", "organizationId", "scoped")}


def sanitize_report(value: Any, key: str = "") -> Any:
    """Remove target identifiers from a report intended for public issue sharing."""
    lowered = key.casefold()
    if lowered == "id" or lowered.endswith("_id") or lowered.endswith("_ids") or lowered in {"team", "organization", "target_team", "target_organization"}:
        return "<redacted>" if value not in (None, "") else value
    if isinstance(value, dict):
        return {child_key: sanitize_report(child, child_key) for child_key, child in value.items()}
    if isinstance(value, list):
        return [sanitize_report(child, key) for child in value]
    return value


class StateStore:
    def __init__(self, path: Path, secrets: tuple[str, ...]) -> None:
        self.path = path
        self.secrets = secrets

    def load(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        try:
            value = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise InstallerError(
                f"Installer state is unreadable: {self.path}",
                code="STATE_INVALID",
                action="Restore the original state file. Do not rerun mutations until existing resources are reconciled.",
                retry_safe=False,
            ) from exc
        if not isinstance(value, dict) or value.get("version") != 1:
            raise InstallerError("Installer state has an unsupported format", code="STATE_INVALID", retry_safe=False)
        return value

    def save(self, value: dict[str, Any]) -> None:
        serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if any(secret and secret in serialized for secret in self.secrets):
            raise InstallerError("Secret-safe state writer rejected output", code="STATE_SECRET_DETECTED", retry_safe=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_name(f"{self.path.name}.tmp")
        temporary.write_text(serialized, encoding="utf-8")
        temporary.replace(self.path)


class Installer:
    def __init__(self, config: Config, make: MakeClient, notion: NotionClient) -> None:
        self.config = config
        self.make = make
        self.notion = notion
        self.state_store = StateStore(config.state_file, config.secrets)
        self.manifest = load_manifest(config.repo_root)
        self.registry = load_registry(config.repo_root, self.manifest)
        self.contracts = data_structure_contracts(self.manifest)
        self.source_connections = source_connection_map(self.registry)
        self.source_structures = source_data_structure_map(self.registry, self.contracts)
        self.source_notion = source_notion_map(self.registry, self.manifest)
        self.source_properties = source_property_maps(self.registry, self.source_notion, self.manifest)
        self.source_scenarios = source_scenario_map(self.registry)
        self.order = dependency_order(self.registry)

    def _new_state(self) -> dict[str, Any]:
        return {
            "version": 1,
            "installation_name": self.config.installation_name,
            "target": {"team_id": self.config.make_team_id, "organization_id": self.config.make_organization_id},
            "canonical_hashes": {key: record["hash"] for key, record in self.registry.items()},
            "data_structures": {},
            "scenarios": {},
            "status": "STARTED",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }

    def _load_state(self) -> dict[str, Any] | None:
        state = self.state_store.load()
        if state is None:
            return None
        expected_target = {"team_id": self.config.make_team_id, "organization_id": self.config.make_organization_id}
        if state.get("target") != expected_target or state.get("installation_name") != self.config.installation_name:
            raise InstallerError(
                "Installer state belongs to a different target or installation name",
                code="STATE_TARGET_MISMATCH",
                action="Use the original configuration or choose a new WEFT_STATE_FILE for a genuinely fresh target.",
                retry_safe=False,
            )
        expected_hashes = {key: record["hash"] for key, record in self.registry.items()}
        if state.get("canonical_hashes") != expected_hashes:
            raise InstallerError(
                "Canonical blueprints changed since this installation began",
                code="STATE_BLUEPRINT_MISMATCH",
                action="Reconcile the partially installed scenarios before intentionally migrating them to new blueprints.",
                retry_safe=False,
            )
        return state

    def _save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = utc_now()
        self.state_store.save(state)

    def _target_checks(self) -> dict[str, Any]:
        read_auth = self.make.request("GET", "/users/me/current-authorization")
        write_auth = self.make.request("GET", "/users/me/current-authorization", write=True)
        team = self.make.unwrap_record(self.make.request("GET", f"/teams/{self.config.make_team_id}"), "team")
        organization = self.make.unwrap_record(self.make.request("GET", f"/organizations/{self.config.make_organization_id}"), "organization")
        if (
            team.get("id") != self.config.make_team_id
            or team.get("organizationId") != self.config.make_organization_id
            or organization.get("id") != self.config.make_organization_id
        ):
            raise InstallerError(
                "Make team and organization do not match the configured target",
                code="TARGET_MISMATCH",
                action="Correct MAKE_TEAM_ID and MAKE_ORGANIZATION_ID before any installation write.",
                retry_safe=False,
            )
        read_scopes = _scope_strings(read_auth)
        write_scopes = _scope_strings(write_auth)
        required_read = ("scenarios:read", "connections:read", "udts:read", "teams:read", "organizations:read")
        required_write = ("scenarios:write", "udts:write")
        missing = [scope for scope in required_read if not _has_scope(read_scopes, scope)]
        missing += [scope for scope in required_write if not _has_scope(write_scopes, scope)]
        if missing:
            raise InstallerError(
                f"Make API token lacks required scopes: {', '.join(missing)}",
                code="MISSING_MAKE_SCOPE",
                action="Create one token with the documented read and write scopes, then rerun preflight.",
                retry_safe=True,
            )
        return {
            "team": {"id": team.get("id"), "name": team.get("name"), "organization_id": team.get("organizationId")},
            "organization": {"id": organization.get("id"), "name": organization.get("name"), "zone": organization.get("zone")},
            "read_scopes": sorted(read_scopes),
            "write_scopes": sorted(write_scopes),
        }

    def _resolve_connection(self, records: list[dict[str, Any]], logical: str) -> dict[str, Any]:
        contract = self.manifest["connections"][logical]
        family = str(contract["family"])
        explicit = self.config.notion_connection_id if logical == "notion" else self.config.ai_connection_id
        matches: list[dict[str, Any]] = []
        for record in records:
            valid = (
                str(record.get("accountName") or "").casefold() == family.casefold()
                and record.get("teamId") == self.config.make_team_id
                and record.get("organizationId") == self.config.make_organization_id
            )
            if logical == "ai_provider":
                valid = valid and record.get("accountType") == "basic" and record.get("scoped") is True
            if valid:
                matches.append(record)
        if explicit is not None:
            selected = [record for record in matches if record.get("id") == explicit]
            if len(selected) == 1:
                return selected[0]
            raise InstallerError(
                f"Configured {logical} connection ID is not a valid target-team {family} connection",
                code="CONNECTION_INVALID",
                resource_type="make_connection",
                candidates=[_safe_connection(record) for record in matches],
                config_key=contract["explicit_config_key"],
                action="Correct the explicit connection ID or leave it empty for unique structural discovery.",
                retry_safe=True,
            )
        if len(matches) == 1:
            return matches[0]
        if logical == "ai_provider" and not matches:
            action = "In Make, open an AI module, add and authorize a Make AI Provider connection, save it, then rerun preflight."
            code = "MANUAL_UI_CONNECTION_REQUIRED"
        elif logical == "notion" and not matches:
            action = "Create and authorize a Make Notion connection in the target team, grant it access to the duplicated databases, then rerun preflight."
            code = "CONNECTION_MISSING"
        else:
            action = f"Set {contract['explicit_config_key']} to the intended valid connection ID."
            code = "CONNECTION_MISSING" if not matches else "CONNECTION_AMBIGUOUS"
        raise InstallerError(
            f"Expected one valid {family} connection; found {len(matches)}",
            code=code,
            resource_type="make_connection",
            candidates=[_safe_connection(record) for record in matches],
            config_key=contract["explicit_config_key"],
            action=action,
            retry_safe=True,
        )

    def _resolve_data_structure_plans(self, discovered: list[dict[str, Any]], state: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
        plans: dict[str, dict[str, Any]] = {}
        state_records = (state or {}).get("data_structures", {})
        for index, (key, contract) in enumerate(self.contracts.items(), 1):
            expected = {"strict": contract["strict"], "spec": contract["spec"]}
            state_record = state_records.get(key) if isinstance(state_records, dict) else None
            if isinstance(state_record, dict) and isinstance(state_record.get("id"), int):
                detail = self.make.get_data_structure(state_record["id"])
                if detail.get("teamId") != self.config.make_team_id or detail.get("name") != contract["name"] or not schemas_compatible(expected, detail):
                    raise InstallerError(
                        f"State Data Structure {key} no longer matches its recorded contract",
                        code="STATE_RESOURCE_DRIFT",
                        resource_type="make_data_structure",
                        candidates=[{"id": detail.get("id"), "name": detail.get("name")}],
                        action="Inspect the recorded resource and restore it; do not create a duplicate.",
                        retry_safe=False,
                    )
                plans[key] = {"action": "reuse_state", "id": state_record["id"], "name": contract["name"]}
                continue
            named = [record for record in discovered if record.get("name") == contract["name"]]
            compatible = [record for record in named if schemas_compatible(expected, record)]
            if len(compatible) == 1 and len(named) == 1:
                plans[key] = {"action": "reuse_exact", "id": compatible[0]["id"], "name": contract["name"]}
            elif not named:
                plans[key] = {"action": "create", "id": 900000000 + index, "name": contract["name"], "synthetic_id": True}
            else:
                raise InstallerError(
                    f"Data Structure name {contract['name']!r} is ambiguous or schema-incompatible",
                    code="DATA_STRUCTURE_AMBIGUOUS",
                    resource_type="make_data_structure",
                    candidates=[{"id": record.get("id"), "name": record.get("name"), "schema_compatible": schemas_compatible(expected, record)} for record in named],
                    action="Keep exactly one schema-compatible installer-named structure, or use the original installer state file.",
                    retry_safe=True,
                )
        return plans

    def _resolve_scenario_plans(self, scenarios: list[dict[str, Any]], state: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
        plans: dict[str, dict[str, Any]] = {}
        state_records = (state or {}).get("scenarios", {})
        for index, key in enumerate(self.order, 1):
            expected_name = f"{self.config.installation_name} - {key}"
            state_record = state_records.get(key) if isinstance(state_records, dict) else None
            if isinstance(state_record, dict) and isinstance(state_record.get("id"), int):
                detail = self.make.get_scenario(state_record["id"])
                if detail.get("teamId") != self.config.make_team_id or detail.get("name") != expected_name:
                    raise InstallerError(
                        f"State scenario {key} no longer matches its recorded identity",
                        code="STATE_RESOURCE_DRIFT",
                        resource_type="make_scenario",
                        candidates=[{"id": detail.get("id"), "name": detail.get("name")}],
                        action="Inspect the recorded scenario and restore its identity; do not create a duplicate.",
                        retry_safe=False,
                    )
                plans[key] = {"action": "reuse_state", "id": state_record["id"], "name": expected_name, "active": detail.get("isActive")}
                continue
            named = [record for record in scenarios if record.get("name") == expected_name]
            if named:
                raise InstallerError(
                    f"Scenario {expected_name!r} exists but is not proven by this installer state",
                    code="UNOWNED_SCENARIO_NAME",
                    resource_type="make_scenario",
                    candidates=[{"id": record.get("id"), "name": record.get("name"), "active": record.get("isActive")} for record in named],
                    action="Restore the matching state file, or manually rename/remove the unowned collision after review.",
                    retry_safe=False,
                )
            plans[key] = {"action": "create", "id": 910000000 + index, "name": expected_name, "synthetic_id": True}
        return plans

    def _build_candidates(
        self,
        connection_ids: dict[str, int],
        structure_ids: dict[str, int],
        scenario_ids: dict[str, int],
        notion_resources: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        candidates: dict[str, dict[str, Any]] = {}
        for key in self.order:
            record = self.registry[key]
            candidate, mutations, unresolved = rebind_blueprint(
                key,
                record["blueprint"],
                source_connections=self.source_connections,
                target_connections=connection_ids,
                source_structures=self.source_structures,
                target_structures=structure_ids,
                source_notion=self.source_notion,
                notion_resources=notion_resources,
                source_properties=self.source_properties,
                source_scenarios=self.source_scenarios,
                target_scenarios=scenario_ids,
                module_overrides=self.manifest.get("module_semantic_overrides", {}),
            )
            candidate["name"] = f"{self.config.installation_name} - {key}"
            validation = validate_candidate(
                key,
                record["blueprint"],
                candidate,
                mutations,
                unresolved,
                source_structures=self.source_structures,
                source_notion=self.source_notion,
                source_scenarios=self.source_scenarios,
                target_connections=connection_ids,
                target_structures=structure_ids,
                notion_resources=notion_resources,
                target_scenarios=scenario_ids,
            )
            if not validation["passed"]:
                raise InstallerError(
                    f"Candidate validation failed for {key}: {validation['failed_checks']}",
                    code="CANDIDATE_VALIDATION_FAILED",
                    resource_type="make_scenario",
                    candidates=[{"scenario": key, "unresolved": unresolved}],
                    action="Compare the canonical export and target Notion schema; do not edit mappings heuristically.",
                    retry_safe=True,
                )
            candidates[key] = {"blueprint": candidate, "mutations": mutations, "validation": validation}
        return candidates

    def preflight(self) -> dict[str, Any]:
        mutation_before = self.make.mutation_count + self.notion.mutation_count
        state = self._load_state()
        target = self._target_checks()
        scenarios = self.make.list_scenarios(self.config.make_team_id)
        connections = self.make.list_connections(self.config.make_team_id)
        structures = self.make.list_data_structures(self.config.make_team_id)
        notion_resources = self.notion.discover_resources(self.manifest["notion_resources"])
        notion_connection = self._resolve_connection(connections, "notion")
        ai_connection = self._resolve_connection(connections, "ai_provider")
        structure_plans = self._resolve_data_structure_plans(structures, state)
        scenario_plans = self._resolve_scenario_plans(scenarios, state)
        connection_ids = {"notion": notion_connection["id"], "ai_provider": ai_connection["id"]}
        structure_ids = {key: plan["id"] for key, plan in structure_plans.items()}
        scenario_ids = {key: plan["id"] for key, plan in scenario_plans.items()}
        candidates = self._build_candidates(connection_ids, structure_ids, scenario_ids, notion_resources)
        mutation_after = self.make.mutation_count + self.notion.mutation_count
        if mutation_after != mutation_before:
            raise InstallerError("Preflight performed an external mutation", code="PREFLIGHT_MUTATION_DETECTED", retry_safe=False)
        return {
            "status": "PREFLIGHT_PASSED",
            "performed_make_mutations": 0,
            "performed_notion_mutations": 0,
            "target": target,
            "state_found": state is not None,
            "connections": {
                "notion": _safe_connection(notion_connection),
                "ai_provider": _safe_connection(ai_connection),
            },
            "notion_resources": notion_resources,
            "data_structure_plans": structure_plans,
            "scenario_plans": scenario_plans,
            "candidate_checks": {key: value["validation"] for key, value in candidates.items()},
            "canonical_hashes": {key: record["hash"] for key, record in self.registry.items()},
            "dependency_order": self.order,
            "known_export_residuals": self.manifest.get("known_export_residuals", []),
        }

    def _provision_data_structures(self, preflight: dict[str, Any], state: dict[str, Any]) -> dict[str, int]:
        result: dict[str, int] = {}
        for key, contract in self.contracts.items():
            plan = preflight["data_structure_plans"][key]
            if plan["action"] in {"reuse_state", "reuse_exact"}:
                structure_id = int(plan["id"])
                state["data_structures"][key] = {"id": structure_id, "name": contract["name"], "status": "REUSED_AND_VERIFIED"}
                self._save_state(state)
                result[key] = structure_id
                continue
            body = {"teamId": self.config.make_team_id, "name": contract["name"], "strict": False, "spec": contract["spec"]}
            structure_id: int | None = None
            try:
                created = self.make.create_data_structure(body)
                if isinstance(created.get("id"), int):
                    structure_id = created["id"]
            except AmbiguousMutationError:
                discovered = self.make.list_data_structures(self.config.make_team_id)
                matches = [item for item in discovered if item.get("name") == contract["name"] and schemas_compatible(body, item)]
                if len(matches) == 1:
                    structure_id = matches[0]["id"]
                else:
                    raise InstallerError(
                        f"Data Structure create outcome for {key} is ambiguous",
                        code="AMBIGUOUS_DATA_STRUCTURE_CREATE",
                        resource_type="make_data_structure",
                        candidates=[{"id": item.get("id"), "name": item.get("name")} for item in matches],
                        action="Inspect the listed structures and restore the state file before retrying.",
                        retry_safe=False,
                    ) from None
            if structure_id is None:
                discovered = self.make.list_data_structures(self.config.make_team_id)
                matches = [item for item in discovered if item.get("name") == contract["name"] and schemas_compatible(body, item)]
                if len(matches) == 1:
                    structure_id = matches[0]["id"]
            if not isinstance(structure_id, int):
                raise InstallerError(
                    f"Make did not return an ID for Data Structure {key}",
                    code="DATA_STRUCTURE_CREATE_FAILED",
                    action="Reconcile by exact installer name before retrying.",
                    retry_safe=False,
                )
            state["data_structures"][key] = {"id": structure_id, "name": contract["name"], "status": "CREATED_UNVERIFIED"}
            self._save_state(state)
            detail = self.make.get_data_structure(structure_id)
            if detail.get("teamId") != self.config.make_team_id or detail.get("name") != contract["name"] or not schemas_compatible(body, detail):
                raise InstallerError(
                    f"Created Data Structure {key} failed read-back verification",
                    code="DATA_STRUCTURE_READBACK_FAILED",
                    resource_type="make_data_structure",
                    candidates=[{"id": structure_id, "name": detail.get("name")}],
                    action="Leave the resource in place and inspect it; the state file makes the next retry deterministic.",
                    retry_safe=False,
                )
            state["data_structures"][key]["status"] = "CREATED_AND_VERIFIED"
            self._save_state(state)
            result[key] = structure_id
        return result

    def _verify_one_scenario(self, key: str, scenario_id: int, candidate: dict[str, Any], expected_name: str, state_owned: bool) -> dict[str, Any]:
        detail = self.make.get_scenario(scenario_id)
        if detail.get("isActive") is True:
            if not state_owned:
                raise InstallerError("Refusing to stop a scenario not recorded in installer state", code="UNOWNED_ACTIVE_SCENARIO", retry_safe=False)
            self.make.stop_scenario(scenario_id)
            detail = self.make.get_scenario(scenario_id)
        stored = extract_readback_blueprint(self.make.get_scenario_blueprint(scenario_id))
        interface = self.make.get_scenario_interface(scenario_id)
        verification = verify_scenario_readback(candidate, detail, stored, interface, expected_name, self.config.make_team_id)
        if not verification["passed"]:
            raise InstallerError(
                f"Scenario {key} failed static read-back: {verification['failed_checks']}",
                code="SCENARIO_READBACK_FAILED",
                resource_type="make_scenario",
                candidates=[{"id": scenario_id, "name": detail.get("name"), "failed_checks": verification["failed_checks"]}],
                action="Leave the inactive scenario in place and inspect the recorded candidate/read-back difference.",
                retry_safe=False,
            )
        return verification

    def _provision_scenarios(
        self,
        preflight: dict[str, Any],
        state: dict[str, Any],
        connection_ids: dict[str, int],
        structure_ids: dict[str, int],
    ) -> dict[str, dict[str, Any]]:
        scenario_ids = {
            key: int(record["id"])
            for key, record in state["scenarios"].items()
            if isinstance(record, dict) and isinstance(record.get("id"), int)
        }
        results: dict[str, dict[str, Any]] = {}
        for key in self.order:
            plan = preflight["scenario_plans"][key]
            target_ids = {**{name: int(value["id"]) for name, value in preflight["scenario_plans"].items()}, **scenario_ids}
            candidates = self._build_candidates(connection_ids, structure_ids, target_ids, preflight["notion_resources"])
            candidate = candidates[key]["blueprint"]
            self._write_candidate_artifacts(key, candidates[key])
            expected_name = plan["name"]
            if plan["action"] == "reuse_state":
                scenario_id = int(plan["id"])
                verification = self._verify_one_scenario(key, scenario_id, candidate, expected_name, state_owned=True)
                state["scenarios"][key]["status"] = "REUSED_AND_VERIFIED"
                self._save_state(state)
                scenario_ids[key] = scenario_id
                results[key] = {"id": scenario_id, "name": expected_name, "status": "REUSED_AND_VERIFIED", "candidate_validation": candidates[key]["validation"], "verification": verification, "inactive": True}
                continue

            scenario_id: int | None = None
            body = make_create_body(candidate, self.config.make_team_id)
            try:
                created = self.make.create_scenario(body)
                if isinstance(created.get("id"), int):
                    scenario_id = created["id"]
            except AmbiguousMutationError:
                matches = [item for item in self.make.list_scenarios(self.config.make_team_id) if item.get("name") == expected_name]
                if len(matches) == 1 and isinstance(matches[0].get("id"), int):
                    scenario_id = matches[0]["id"]
                else:
                    raise InstallerError(
                        f"Scenario create outcome for {key} is ambiguous",
                        code="AMBIGUOUS_SCENARIO_CREATE",
                        resource_type="make_scenario",
                        candidates=[{"id": item.get("id"), "name": item.get("name")} for item in matches],
                        action="Inspect exact-name scenarios and restore the state file before retrying.",
                        retry_safe=False,
                    ) from None
            if scenario_id is None:
                matches = [item for item in self.make.list_scenarios(self.config.make_team_id) if item.get("name") == expected_name]
                if len(matches) == 1 and isinstance(matches[0].get("id"), int):
                    scenario_id = matches[0]["id"]
            if not isinstance(scenario_id, int):
                raise InstallerError(
                    f"Make did not return an ID for scenario {key}",
                    code="SCENARIO_CREATE_FAILED",
                    action="Reconcile exact-name scenarios before retrying.",
                    retry_safe=False,
                )
            state["scenarios"][key] = {"id": scenario_id, "name": expected_name, "status": "CREATED_UNVERIFIED"}
            self._save_state(state)
            scenario_ids[key] = scenario_id
            verification = self._verify_one_scenario(key, scenario_id, candidate, expected_name, state_owned=True)
            state["scenarios"][key]["status"] = "CREATED_AND_VERIFIED"
            self._save_state(state)
            results[key] = {"id": scenario_id, "name": expected_name, "status": "CREATED_AND_VERIFIED", "candidate_validation": candidates[key]["validation"], "verification": verification, "inactive": True}
        return results

    def _write_candidate_artifacts(self, key: str, record: dict[str, Any]) -> None:
        directory = self.config.state_file.parent / "candidates"
        directory.mkdir(parents=True, exist_ok=True)
        artifacts = (
            (f"{key}.candidate.json", record["blueprint"]),
            (
                f"{key}.binding-manifest.json",
                {
                    "scenario": key,
                    "canonical_hash": self.registry[key]["hash"],
                    "mutations": record["mutations"],
                    "validation": record["validation"],
                    "contains_secrets": False,
                },
            ),
        )
        for name, value in artifacts:
            serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            if any(secret and secret in serialized for secret in self.config.secrets):
                raise InstallerError("Secret-safe candidate writer rejected output", code="REPORT_SECRET_DETECTED", retry_safe=False)
            (directory / name).write_text(serialized, encoding="utf-8")

    def install(self) -> dict[str, Any]:
        preflight = self.preflight()
        state = self._load_state() or self._new_state()
        self._save_state(state)
        mutation_start = self.make.mutation_count
        structure_ids = self._provision_data_structures(preflight, state)
        connection_ids = {
            "notion": int(preflight["connections"]["notion"]["id"]),
            "ai_provider": int(preflight["connections"]["ai_provider"]["id"]),
        }
        scenario_results = self._provision_scenarios(preflight, state, connection_ids, structure_ids)
        final_hashes = {key: file_hash(record["path"]) for key, record in self.registry.items()}
        if final_hashes != state["canonical_hashes"]:
            raise InstallerError("Canonical blueprints changed during installation", code="CANONICAL_MUTATION_DETECTED", retry_safe=False)
        if not all(result.get("inactive") is True for result in scenario_results.values()):
            raise InstallerError("Not all installed scenarios are inactive", code="ACTIVE_SCENARIO_REMAINED", retry_safe=False)
        state["status"] = "LOCALLY_VERIFIED_CLEAN_INSTALL_PENDING"
        self._save_state(state)
        report = {
            "status": state["status"],
            "completed_at": utc_now(),
            "target": copy.deepcopy(state["target"]),
            "installation_name": self.config.installation_name,
            "data_structures": copy.deepcopy(state["data_structures"]),
            "scenarios": scenario_results,
            "dependency_rebindings": [
                {"scenario": key, "dependency": dependency, "scenario_id": scenario_results[dependency]["id"]}
                for key, record in self.registry.items()
                for dependency in record.get("dependencies", [])
            ],
            "verification": {
                "canonical_files_unchanged": True,
                "static_readback_passed": True,
                "all_scenarios_inactive": True,
                "runtime_tests_executed": False,
                "clean_environment_acceptance": "pending",
            },
            "external_mutation_attempts_this_run": self.make.mutation_count - mutation_start,
            "manual_actions_remaining": [
                "Configure MCP exposure and clients for the three public scenarios.",
                "Run clean-install scenario and client acceptance tests with sanitized data.",
                "Configure and activate create_daily_log only if the optional workflow is required."
            ],
            "safe_retry": "Rerun with the same configuration and state file; recorded resources are read back before reuse.",
        }
        self._write_reports(report)
        return report

    def write_preflight_report(self, report: dict[str, Any]) -> None:
        directory = self.config.state_file.parent
        directory.mkdir(parents=True, exist_ok=True)
        raw_path = directory / "preflight-report.json"
        safe_path = directory / "preflight-report.sanitized.json"
        for path, value in ((raw_path, report), (safe_path, sanitize_report(report))):
            serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            if any(secret and secret in serialized for secret in self.config.secrets):
                raise InstallerError("Secret-safe preflight writer rejected output", code="REPORT_SECRET_DETECTED", retry_safe=False)
            path.write_text(serialized, encoding="utf-8")

    def record_failure(self, error: InstallerError) -> None:
        state = self.state_store.load()
        if state is not None:
            state["status"] = "BLOCKED"
            state["last_error"] = error.to_dict()
            self._save_state(state)
        directory = self.config.state_file.parent
        directory.mkdir(parents=True, exist_ok=True)
        payload = {"failed_at": utc_now(), **error.to_dict()}
        for name, value in (("installation-error.json", payload), ("installation-error.sanitized.json", sanitize_report(payload))):
            serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            if any(secret and secret in serialized for secret in self.config.secrets):
                raise InstallerError("Secret-safe failure writer rejected output", code="REPORT_SECRET_DETECTED", retry_safe=False)
            (directory / name).write_text(serialized, encoding="utf-8")

    def _write_reports(self, report: dict[str, Any]) -> None:
        directory = self.config.state_file.parent
        directory.mkdir(parents=True, exist_ok=True)
        for name, value in (
            ("installation-report.json", report),
            ("installation-report.sanitized.json", sanitize_report(report)),
        ):
            serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
            if any(secret and secret in serialized for secret in self.config.secrets):
                raise InstallerError("Secret-safe report writer rejected output", code="REPORT_SECRET_DETECTED", retry_safe=False)
            (directory / name).write_text(serialized, encoding="utf-8")
