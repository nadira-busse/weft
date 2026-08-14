"""Structural inspection, rebinding, and candidate verification.

All replacements are made at typed Make blueprint paths. This module never
performs unrestricted serialized-text replacement.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

from .errors import InstallerError


FILTER_DELIMITER = " |&*^%$#@| "
PROPERTY_TOKEN_RE = re.compile(
    r"(?P<module>\d+)\.properties_value\.(?:`(?P<quoted>[^`]+)`|(?P<plain>[A-Za-z0-9_]+))"
)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallerError(f"Invalid or unavailable JSON: {path}", code="INVALID_PUBLIC_ARTIFACT", retry_safe=True) from exc


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def json_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold().replace("_", " ")).strip()


def walk_modules(value: Any, path: str = "$") -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        if isinstance(value.get("id"), int) and isinstance(value.get("module"), str):
            yield path, value
        for key, child in value.items():
            yield from walk_modules(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_modules(child, f"{path}[{index}]")


def module_by_id(blueprint: dict[str, Any], module_id: int) -> dict[str, Any]:
    matches = [module for _, module in walk_modules(blueprint) if module.get("id") == module_id]
    if len(matches) != 1:
        raise InstallerError(f"Expected one module {module_id}; found {len(matches)}", code="BLUEPRINT_STRUCTURE_CHANGED")
    return matches[0]


def topology(blueprint: dict[str, Any]) -> list[tuple[str, int, str]]:
    return [(path, module["id"], module["module"]) for path, module in walk_modules(blueprint)]


def output_interface(blueprint: dict[str, Any]) -> Any:
    io = blueprint.get("io")
    return copy.deepcopy(io) if isinstance(io, dict) else None


def connection_locations(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path, module in walk_modules(blueprint):
        parameters = module.get("parameters") if isinstance(module.get("parameters"), dict) else {}
        for key in ("__IMTCONN__", "makeConnectionId"):
            value = parameters.get(key)
            if value not in (None, ""):
                package = str(module["module"]).split(":", 1)[0]
                family = "notion" if package == "notion" else "ai_provider" if package == "ai-tools" else None
                found.append({"path": f"{path}.parameters.{key}", "module_id": module["id"], "key": key, "value": value, "family": family})
    return found


def data_structure_locations(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path, module in walk_modules(blueprint):
        parameters = module.get("parameters") if isinstance(module.get("parameters"), dict) else {}
        if module.get("module") not in {"json:CreateJSON", "json:ParseJSON"} or parameters.get("type") in (None, ""):
            continue
        restored = (((module.get("metadata") or {}).get("restore") or {}).get("parameters") or {}).get("type") or {}
        found.append({
            "path": f"{path}.parameters.type",
            "module_id": module["id"],
            "value": parameters["type"],
            "label": restored.get("label") if isinstance(restored, dict) else None,
        })
    return found


def scenario_reference_locations(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path, module in walk_modules(blueprint):
        parameters = module.get("parameters") if isinstance(module.get("parameters"), dict) else {}
        for key, value in parameters.items():
            if key.casefold() in {"scenario", "scenarioid", "scenario_id"} and isinstance(value, (str, int)):
                found.append({"path": f"{path}.parameters.{key}", "module_id": module["id"], "key": key, "value": value})
    return found


def notion_locations(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for path, module in walk_modules(blueprint):
        if not str(module.get("module", "")).startswith("notion:"):
            continue
        mapper = module.get("mapper") if isinstance(module.get("mapper"), dict) else {}
        restored = (((module.get("metadata") or {}).get("restore") or {}).get("expect") or {}).get("data_source") or {}
        rpc = restored.get("rpcSearch") if isinstance(restored.get("rpcSearch"), dict) else {}
        found.append({
            "path": path,
            "module_id": module["id"],
            "value": mapper.get("data_source"),
            "label": rpc.get("label") if isinstance(rpc.get("label"), str) else None,
        })
    return found


def load_manifest(repo_root: Path) -> dict[str, Any]:
    manifest = load_json(repo_root / "installer" / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("version") != 1:
        raise InstallerError("installer/manifest.json has an unsupported version", code="INVALID_PUBLIC_ARTIFACT")
    if len(manifest.get("scenarios", [])) != 5 or len(manifest.get("data_structures", [])) != 4:
        raise InstallerError("Installer manifest must define exactly five scenarios and four Data Structures", code="INVALID_PUBLIC_ARTIFACT")
    return manifest


def load_registry(repo_root: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    registry: dict[str, dict[str, Any]] = {}
    for record in manifest["scenarios"]:
        key = record.get("key")
        path = (repo_root / str(record.get("blueprint", ""))).resolve()
        try:
            path.relative_to(repo_root.resolve())
        except ValueError as exc:
            raise InstallerError(f"Blueprint path escapes the repository: {path}", code="INVALID_PUBLIC_ARTIFACT") from exc
        blueprint = load_json(path)
        if not isinstance(blueprint, dict) or not isinstance(blueprint.get("flow"), list):
            raise InstallerError(f"{path.name} is not a Make scenario blueprint", code="INVALID_PUBLIC_ARTIFACT")
        expected_name = f"weft_{key}"
        if blueprint.get("name") != expected_name:
            raise InstallerError(
                f"Blueprint identity mismatch for {key}: expected root name {expected_name!r}",
                code="BLUEPRINT_STRUCTURE_CHANGED",
            )
        modules = list(walk_modules(blueprint))
        ids = [module["id"] for _, module in modules]
        if len(ids) != len(set(ids)):
            raise InstallerError(f"Duplicate module IDs in {path.name}", code="BLUEPRINT_STRUCTURE_CHANGED")
        refs = scenario_reference_locations(blueprint)
        dependencies = record.get("dependencies", [])
        if bool(refs) != bool(dependencies):
            raise InstallerError(f"Dependency manifest disagrees with {path.name}", code="DEPENDENCY_GRAPH_CHANGED")
        registry[str(key)] = {**record, "path": path, "blueprint": blueprint, "hash": file_hash(path)}
    if len(registry) != 5:
        raise InstallerError("Scenario keys in installer manifest are not unique", code="INVALID_PUBLIC_ARTIFACT")
    return registry


def normalize_make_schema(value: Any) -> Any:
    if isinstance(value, list):
        return [normalize_make_schema(item) for item in value]
    if isinstance(value, dict):
        allowed = ("name", "type", "required", "spec")
        normalized = {key: normalize_make_schema(value[key]) for key in allowed if key in value and value[key] is not None}
        if "type" in normalized and "required" not in normalized:
            normalized["required"] = False
        return normalized
    return value


def schemas_compatible(expected: dict[str, Any], actual: dict[str, Any]) -> bool:
    return (
        isinstance(actual, dict)
        and bool(actual)
        and bool(expected)
        and actual.get("strict", False) is expected.get("strict", False)
        and normalize_make_schema(actual.get("spec", [])) == normalize_make_schema(expected.get("spec", []))
    )


def data_structure_contracts(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for item in manifest["data_structures"]:
        key = str(item["key"])
        spec = normalize_make_schema(item.get("spec", []))
        if not isinstance(spec, list) or not spec:
            raise InstallerError(f"Data Structure {key} has no schema", code="INVALID_PUBLIC_ARTIFACT")
        result[key] = {**item, "strict": False, "spec": spec}
    return result


def source_data_structure_map(registry: dict[str, dict[str, Any]], contracts: dict[str, dict[str, Any]]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for key, contract in contracts.items():
        for label in contract.get("source_labels", []):
            labels[normalize_name(str(label))] = key
    mapping: dict[str, set[str]] = defaultdict(set)
    for record in registry.values():
        for location in data_structure_locations(record["blueprint"]):
            logical = labels.get(normalize_name(str(location.get("label") or "")))
            if not logical:
                raise InstallerError(
                    f"Unknown Data Structure label {location.get('label')!r} in {record['path'].name}",
                    code="BLUEPRINT_STRUCTURE_CHANGED",
                )
            mapping[str(location["value"])].add(logical)
    ambiguous = {source: sorted(values) for source, values in mapping.items() if len(values) != 1}
    if ambiguous:
        raise InstallerError(f"Ambiguous source Data Structure mappings: {ambiguous}", code="BLUEPRINT_STRUCTURE_CHANGED")
    return {source: next(iter(values)) for source, values in mapping.items()}


def source_notion_map(registry: dict[str, dict[str, Any]], manifest: dict[str, Any]) -> dict[str, str]:
    aliases = {normalize_name(key): value for key, value in manifest["notion_aliases"].items()}
    mapping: dict[str, set[str]] = defaultdict(set)
    for record in registry.values():
        for location in notion_locations(record["blueprint"]):
            source = location.get("value")
            label = location.get("label")
            if not source or not label:
                continue
            semantic = aliases.get(normalize_name(label))
            if not semantic:
                raise InstallerError(f"Unknown Notion resource label {label!r}", code="BLUEPRINT_STRUCTURE_CHANGED")
            mapping[str(source)].add(semantic)
    ambiguous = {source: sorted(values) for source, values in mapping.items() if len(values) != 1}
    if ambiguous:
        raise InstallerError(f"Ambiguous source Notion mappings: {ambiguous}", code="BLUEPRINT_STRUCTURE_CHANGED")
    return {source: next(iter(values)) for source, values in mapping.items()}


def source_property_maps(
    registry: dict[str, dict[str, Any]],
    source_notion: dict[str, str],
    manifest: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Build an exported property-ID to semantic-name map across peer modules.

    Some Make modules export only editor state for their selected fields, while
    another module for the same data source exports the complete field labels.
    Joining those exports by semantic data source makes rebinding deterministic.
    """
    result: dict[str, dict[str, str]] = defaultdict(dict)
    conflicts: list[dict[str, str]] = []
    overrides = manifest.get("module_semantic_overrides", {})
    for scenario_key, record in registry.items():
        for _, module in walk_modules(record["blueprint"]):
            if not str(module.get("module", "")).startswith("notion:"):
                continue
            semantic = _module_semantic(module, source_notion, overrides.get(scenario_key, {}))
            if not semantic:
                continue
            for source_id, spec in _metadata_field_specs(module).items():
                label = spec.get("label")
                if not isinstance(label, str) or not label:
                    continue
                previous = result[semantic].get(source_id)
                if previous and normalize_name(previous) != normalize_name(label):
                    conflicts.append({"resource": semantic, "property_id": source_id, "first": previous, "second": label})
                result[semantic][source_id] = label
    if conflicts:
        raise InstallerError(f"Conflicting exported Notion property labels: {conflicts}", code="BLUEPRINT_STRUCTURE_CHANGED")
    return {semantic: dict(values) for semantic, values in result.items()}


def source_connection_map(registry: dict[str, dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, set[str]] = defaultdict(set)
    for record in registry.values():
        for location in connection_locations(record["blueprint"]):
            family = location.get("family")
            if not family:
                raise InstallerError(
                    f"Unsupported connection-bearing module at {record['key']} module {location['module_id']}",
                    code="BLUEPRINT_STRUCTURE_CHANGED",
                )
            mapping[str(location["value"])].add(str(family))
    ambiguous = {source: sorted(values) for source, values in mapping.items() if len(values) != 1}
    if ambiguous:
        raise InstallerError(f"Ambiguous source connection mappings: {ambiguous}", code="BLUEPRINT_STRUCTURE_CHANGED")
    return {source: next(iter(values)) for source, values in mapping.items()}


def source_scenario_map(registry: dict[str, dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, set[str]] = defaultdict(set)
    for key, record in registry.items():
        dependencies = [str(item) for item in record.get("dependencies", [])]
        refs = scenario_reference_locations(record["blueprint"])
        if refs and len(dependencies) != 1:
            raise InstallerError(f"{key} dependency references are not uniquely declared", code="DEPENDENCY_GRAPH_CHANGED")
        for location in refs:
            mapping[str(location["value"])].add(dependencies[0])
    ambiguous = {source: sorted(values) for source, values in mapping.items() if len(values) != 1}
    if ambiguous:
        raise InstallerError(f"Ambiguous source scenario references: {ambiguous}", code="DEPENDENCY_GRAPH_CHANGED")
    return {source: next(iter(values)) for source, values in mapping.items()}


def dependency_order(registry: dict[str, dict[str, Any]]) -> list[str]:
    remaining = {key: set(map(str, record.get("dependencies", []))) for key, record in registry.items()}
    order: list[str] = []
    while remaining:
        ready = [key for key in registry if key in remaining and not remaining[key]]
        if not ready:
            raise InstallerError(f"Scenario dependency cycle: {sorted(remaining)}", code="DEPENDENCY_GRAPH_CHANGED")
        for key in ready:
            order.append(key)
            remaining.pop(key)
        for values in remaining.values():
            values.difference_update(ready)
    return order


def _match_property(label: str, resource: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    matches = [
        (name, prop)
        for name, prop in resource.get("properties", {}).items()
        if normalize_name(name) == normalize_name(label)
    ]
    return matches[0] if len(matches) == 1 else None


def _match_property_id(property_id: str, resource: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    matches = [(name, prop) for name, prop in resource.get("properties", {}).items() if str(prop.get("id")) == str(property_id)]
    return matches[0] if len(matches) == 1 else None


def _metadata_field_specs(module: dict[str, Any]) -> dict[str, dict[str, Any]]:
    data_source = (((module.get("metadata") or {}).get("restore") or {}).get("expect") or {}).get("data_source") or {}
    result: dict[str, dict[str, Any]] = {}
    for item in data_source.get("nested", []) if isinstance(data_source, dict) else []:
        if isinstance(item, dict):
            for spec in item.get("spec", []):
                if isinstance(spec, dict) and isinstance(spec.get("name"), str):
                    result[spec["name"]] = spec
    return result


def _module_semantic(module: dict[str, Any], source_semantics: dict[str, str], overrides: dict[str, str]) -> str | None:
    mapper = module.get("mapper") if isinstance(module.get("mapper"), dict) else {}
    source = mapper.get("data_source")
    if isinstance(source, str) and source in source_semantics:
        return source_semantics[source]
    restored = (((module.get("metadata") or {}).get("restore") or {}).get("expect") or {}).get("data_source") or {}
    rpc = restored.get("rpcSearch") if isinstance(restored, dict) else None
    label = rpc.get("label") if isinstance(rpc, dict) else None
    if isinstance(label, str):
        matches = [value for value in set(source_semantics.values()) if normalize_name(value) == normalize_name(label)]
        if len(matches) == 1:
            return matches[0]
    return overrides.get(str(module.get("id")))


def _record(mutations: list[dict[str, Any]], category: str, path: str, before: Any, after: Any, module_id: int | None = None) -> None:
    if before != after:
        mutations.append({"category": category, "path": path, "before": before, "after": after, "module_id": module_id})


def _replace_relation_ids(value: Any, path: str, replacements: dict[str, str], mutations: list[dict[str, Any]], module_id: int) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if isinstance(child, str):
                updated = child
                for source, target in replacements.items():
                    if source in updated:
                        updated = updated.replace(source, target)
                if updated != child:
                    value[key] = updated
                    _record(mutations, "notion_relation_metadata", child_path, child, updated, module_id)
            else:
                _replace_relation_ids(child, child_path, replacements, mutations, module_id)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            if isinstance(child, str):
                updated = child
                for source, target in replacements.items():
                    if source in updated:
                        updated = updated.replace(source, target)
                if updated != child:
                    value[index] = updated
                    _record(mutations, "notion_relation_metadata", child_path, child, updated, module_id)
            else:
                _replace_relation_ids(child, child_path, replacements, mutations, module_id)


def _update_metadata_fields(value: Any, path: str, property_map: dict[str, tuple[str, dict[str, Any]]], mutations: list[dict[str, Any]], module_id: int) -> None:
    if isinstance(value, dict):
        rebuilt: dict[str, Any] = {}
        for key, child in value.items():
            match = property_map.get(key)
            new_key = str(match[1]["id"]) if match else key
            rebuilt[new_key] = child
            _record(mutations, "notion_property_metadata_key", f"{path}.{key}", key, new_key, module_id)
        if list(rebuilt) != list(value):
            value.clear()
            value.update(rebuilt)
        name = value.get("name")
        match = property_map.get(name) if isinstance(name, str) else None
        if match:
            before = value["name"]
            value["name"] = str(match[1]["id"])
            _record(mutations, "notion_property_metadata", f"{path}.name", before, value["name"], module_id)
            if "label" in value:
                before_label = value["label"]
                value["label"] = match[0]
                _record(mutations, "notion_property_metadata", f"{path}.label", before_label, value["label"], module_id)
        for key, child in list(value.items()):
            _update_metadata_fields(child, f"{path}.{key}", property_map, mutations, module_id)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _update_metadata_fields(child, f"{path}[{index}]", property_map, mutations, module_id)


def _rewrite_tokens(value: Any, path: str, semantics: dict[int, str], resources: dict[str, Any], mutations: list[dict[str, Any]], unresolved: list[dict[str, Any]]) -> Any:
    if isinstance(value, dict):
        for key, child in value.items():
            value[key] = _rewrite_tokens(child, f"{path}.{key}", semantics, resources, mutations, unresolved)
        return value
    if isinstance(value, list):
        for index, child in enumerate(value):
            value[index] = _rewrite_tokens(child, f"{path}[{index}]", semantics, resources, mutations, unresolved)
        return value
    if not isinstance(value, str):
        return value

    def replacement(match: re.Match[str]) -> str:
        module_id = int(match.group("module"))
        raw = match.group("quoted") or match.group("plain") or ""
        semantic = semantics.get(module_id)
        prop = _match_property(raw, resources[semantic]) if semantic in resources else None
        if not prop:
            unresolved.append({"category": "notion_output_token", "path": path, "module_id": module_id, "property": raw})
            return match.group(0)
        updated = f"{module_id}.properties_value.`{prop[0]}`"
        _record(mutations, "notion_output_token", path, match.group(0), updated, module_id)
        return updated

    return PROPERTY_TOKEN_RE.sub(replacement, value)


def rebind_blueprint(
    scenario_key: str,
    canonical: dict[str, Any],
    *,
    source_connections: dict[str, str],
    target_connections: dict[str, int],
    source_structures: dict[str, str],
    target_structures: dict[str, int],
    source_notion: dict[str, str],
    notion_resources: dict[str, Any],
    source_properties: dict[str, dict[str, str]],
    source_scenarios: dict[str, str],
    target_scenarios: dict[str, int],
    module_overrides: dict[str, dict[str, str]],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    candidate = copy.deepcopy(canonical)
    mutations: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    overrides = module_overrides.get(scenario_key, {})
    target_notion = {key: str(value["data_source_id"]) for key, value in notion_resources.items()}
    notion_id_map = {source: target_notion[semantic] for source, semantic in source_notion.items() if semantic in target_notion}
    module_semantics: dict[int, str] = {}

    for path, module in walk_modules(candidate):
        module_id = module["id"]
        parameters = module.get("parameters") if isinstance(module.get("parameters"), dict) else {}
        for key in ("__IMTCONN__", "makeConnectionId"):
            if parameters.get(key) in (None, ""):
                continue
            before = parameters[key]
            family = source_connections.get(str(before))
            target = target_connections.get(str(family)) if family else None
            if not isinstance(target, int):
                unresolved.append({"category": "connection", "path": f"{path}.parameters.{key}", "module_id": module_id, "source": before, "family": family})
            else:
                parameters[key] = target
                _record(mutations, "connection", f"{path}.parameters.{key}", before, target, module_id)

        if module.get("module") in {"json:CreateJSON", "json:ParseJSON"} and parameters.get("type") not in (None, ""):
            before = parameters["type"]
            logical = source_structures.get(str(before))
            target = target_structures.get(str(logical)) if logical else None
            if not isinstance(target, int):
                unresolved.append({"category": "data_structure", "path": f"{path}.parameters.type", "module_id": module_id, "source": before, "logical": logical})
            else:
                parameters["type"] = target
                _record(mutations, "data_structure", f"{path}.parameters.type", before, target, module_id)

        if not str(module.get("module", "")).startswith("notion:"):
            continue
        semantic = _module_semantic(module, source_notion, overrides)
        if semantic:
            module_semantics[module_id] = semantic
        mapper = module.get("mapper") if isinstance(module.get("mapper"), dict) else {}
        if isinstance(mapper.get("data_source"), str):
            before = mapper["data_source"]
            target = notion_id_map.get(before)
            if not target:
                unresolved.append({"category": "notion_data_source", "path": f"{path}.mapper.data_source", "module_id": module_id, "source": before, "semantic": semantic})
            else:
                mapper["data_source"] = target
                _record(mutations, "notion_data_source", f"{path}.mapper.data_source", before, target, module_id)

        restored = (((module.get("metadata") or {}).get("restore") or {}).get("expect") or {}).get("data_source")
        if isinstance(restored, dict):
            _replace_relation_ids(restored, f"{path}.metadata.restore.expect.data_source", notion_id_map, mutations, module_id)
            rpc = restored.get("rpcSearch")
            if isinstance(rpc, dict) and semantic in notion_resources:
                before = rpc.get("value")
                rpc["value"] = notion_resources[semantic]["data_source_id"]
                rpc["label"] = notion_resources[semantic].get("title", semantic)
                _record(mutations, "notion_data_source_metadata", f"{path}.metadata.restore.expect.data_source.rpcSearch.value", before, rpc["value"], module_id)

        if semantic not in notion_resources:
            if mapper.get("fields") or mapper.get("filter"):
                unresolved.append({"category": "notion_module_semantic", "path": path, "module_id": module_id})
            continue
        resource = notion_resources[semantic]
        property_map: dict[str, tuple[str, dict[str, Any]]] = {}
        for old_id, spec in _metadata_field_specs(module).items():
            match = _match_property(str(spec.get("label") or ""), resource)
            if match:
                property_map[old_id] = match
        fields = mapper.get("fields") if isinstance(mapper.get("fields"), dict) else {}
        if fields:
            rebuilt: dict[str, Any] = {}
            for old_id, field_value in fields.items():
                semantic_label = source_properties.get(str(semantic), {}).get(old_id)
                match = property_map.get(old_id)
                if not match and semantic_label:
                    match = _match_property(semantic_label, resource)
                if not match:
                    match = _match_property_id(old_id, resource)
                if not match:
                    unresolved.append({"category": "notion_property", "path": f"{path}.mapper.fields.{old_id}", "module_id": module_id})
                    rebuilt[old_id] = field_value
                    continue
                property_map[old_id] = match
                new_id = str(match[1]["id"])
                rebuilt[new_id] = field_value
                _record(mutations, "notion_property", f"{path}.mapper.fields.{old_id}", old_id, new_id, module_id)
            mapper["fields"] = rebuilt
        _update_metadata_fields(module.get("metadata") or {}, f"{path}.metadata", property_map, mutations, module_id)

        filters = mapper.get("filter") if isinstance(mapper.get("filter"), list) else []
        for group_index, group in enumerate(filters):
            if not isinstance(group, list):
                continue
            for filter_index, condition in enumerate(group):
                if not isinstance(condition, dict) or not isinstance(condition.get("a"), str):
                    continue
                raw = condition["a"].split(FILTER_DELIMITER, 1)[0]
                match = _match_property(raw, resource)
                if not match:
                    unresolved.append({"category": "notion_filter_property", "path": f"{path}.mapper.filter[{group_index}][{filter_index}].a", "module_id": module_id, "property": raw})
                    continue
                before = condition["a"]
                condition["a"] = f"{match[0]}{FILTER_DELIMITER}{match[1]['type']}"
                _record(mutations, "notion_filter_property", f"{path}.mapper.filter[{group_index}][{filter_index}].a", before, condition["a"], module_id)

    for path, module in walk_modules(candidate):
        parameters = module.get("parameters") if isinstance(module.get("parameters"), dict) else {}
        for key, value in list(parameters.items()):
            if key.casefold() not in {"scenario", "scenarioid", "scenario_id"}:
                continue
            dependency = source_scenarios.get(str(value))
            target = target_scenarios.get(str(dependency)) if dependency else None
            if not isinstance(target, int):
                unresolved.append({"category": "scenario_reference", "path": f"{path}.parameters.{key}", "module_id": module["id"], "source": value, "dependency": dependency})
            else:
                parameters[key] = f"SCN_{target}"
                _record(mutations, "scenario_reference", f"{path}.parameters.{key}", value, parameters[key], module["id"])

    _rewrite_tokens(candidate, "$", module_semantics, notion_resources, mutations, unresolved)
    unique: dict[tuple[str, str, str], dict[str, Any]] = {}
    for item in unresolved:
        key = (str(item.get("category")), str(item.get("path")), str(item.get("source", item.get("property", ""))))
        unique.setdefault(key, item)
    return candidate, mutations, list(unique.values())


def validate_candidate(
    scenario_key: str,
    canonical: dict[str, Any],
    candidate: dict[str, Any],
    mutations: list[dict[str, Any]],
    unresolved: list[dict[str, Any]],
    *,
    source_structures: dict[str, str],
    source_notion: dict[str, str],
    source_scenarios: dict[str, str],
    target_connections: dict[str, int],
    target_structures: dict[str, int],
    notion_resources: dict[str, Any],
    target_scenarios: dict[str, int],
) -> dict[str, Any]:
    checks: dict[str, bool] = {
        "no_unresolved_bindings": not unresolved,
        "topology_unchanged": topology(canonical) == topology(candidate),
        "public_interface_unchanged": output_interface(canonical) == output_interface(candidate),
    }
    canonical_connections = {item["path"]: item for item in connection_locations(canonical)}
    candidate_connections = {item["path"]: item for item in connection_locations(candidate)}
    checks["connections_resolved"] = (
        candidate_connections.keys() == canonical_connections.keys()
        and all(
            item.get("family") in target_connections
            and item["value"] == target_connections[item["family"]]
            for item in candidate_connections.values()
        )
    )

    canonical_structures = {item["path"]: item for item in data_structure_locations(canonical)}
    candidate_structures = {item["path"]: item for item in data_structure_locations(candidate)}
    checks["data_structures_resolved"] = (
        candidate_structures.keys() == canonical_structures.keys()
        and all(
            source_structures.get(str(canonical_structures[path]["value"])) in target_structures
            and item["value"] == target_structures[source_structures[str(canonical_structures[path]["value"])]]
            for path, item in candidate_structures.items()
        )
    )

    canonical_notion = {item["path"]: item for item in notion_locations(canonical)}
    candidate_notion = {item["path"]: item for item in notion_locations(candidate)}
    checks["notion_sources_resolved"] = (
        candidate_notion.keys() == canonical_notion.keys()
        and all(
            (not canonical_notion[path].get("value") and not item.get("value"))
            or (
                source_notion.get(str(canonical_notion[path].get("value"))) in notion_resources
                and str(item.get("value"))
                == str(notion_resources[source_notion[str(canonical_notion[path]["value"])]] ["data_source_id"])
            )
            for path, item in candidate_notion.items()
        )
    )

    canonical_refs = {item["path"]: item for item in scenario_reference_locations(canonical)}
    candidate_refs = {item["path"]: item for item in scenario_reference_locations(candidate)}
    checks["scenario_dependencies_resolved"] = (
        candidate_refs.keys() == canonical_refs.keys()
        and all(
            source_scenarios.get(str(canonical_refs[path]["value"])) in target_scenarios
            and str(item["value"])
            == f"SCN_{target_scenarios[source_scenarios[str(canonical_refs[path]['value'])]]}"
            for path, item in candidate_refs.items()
        )
    )

    if scenario_key == "create_daily_log":
        module_14 = module_by_id(candidate, 14)
        filter_value = (module_14.get("mapper") or {}).get("filter")
        checks["daily_log_filter_preserved"] = canonical_json(filter_value) == canonical_json((module_by_id(canonical, 14).get("mapper") or {}).get("filter"))
        module_43 = module_by_id(candidate, 43)
        checks["ai_provider_and_model_preserved"] = module_43.get("module") == "ai-tools:Ask" and (module_43.get("parameters") or {}).get("model") == "small"

    failed = [name for name, passed in checks.items() if not passed]
    return {
        "passed": not failed,
        "candidate_mode": "rebound" if mutations else "no_op",
        "checks": checks,
        "failed_checks": failed,
        "mutation_count": len(mutations),
        "mutation_categories": dict(sorted(Counter(item["category"] for item in mutations).items())),
        "unresolved": unresolved,
        "global_string_replacement_used": False,
    }


def make_create_body(candidate: dict[str, Any], team_id: int) -> dict[str, Any]:
    submitted = copy.deepcopy(candidate)
    interface = submitted.pop("io", None)
    body: dict[str, Any] = {
        "blueprint": json.dumps(submitted, ensure_ascii=False, separators=(",", ":")),
        "teamId": team_id,
        "scheduling": json.dumps({"type": "on-demand"}, separators=(",", ":")),
    }
    if interface is not None:
        if not isinstance(interface, dict) or not isinstance(interface.get("input_spec"), list) or not isinstance(interface.get("output_spec"), list):
            raise InstallerError("Blueprint io is malformed", code="BLUEPRINT_STRUCTURE_CHANGED")
        body["metadata"] = {
            "input_spec": copy.deepcopy(interface["input_spec"]),
            "output_spec": copy.deepcopy(interface["output_spec"]),
        }
    return body


def extract_readback_blueprint(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict) and isinstance(payload.get("blueprint"), str):
        return json.loads(payload["blueprint"])
    if isinstance(payload, dict) and isinstance(payload.get("blueprint"), dict):
        nested = payload["blueprint"]
        if isinstance(nested.get("blueprint"), str):
            return json.loads(nested["blueprint"])
        if isinstance(nested.get("flow"), list):
            return nested
    if isinstance(payload, dict) and isinstance(payload.get("response"), dict):
        return extract_readback_blueprint(payload["response"])
    raise InstallerError("Scenario blueprint read-back is missing", code="READBACK_FAILED", retry_safe=True)


def verify_scenario_readback(candidate: dict[str, Any], detail: dict[str, Any], blueprint: dict[str, Any], interface: dict[str, Any] | None, expected_name: str, team_id: int) -> dict[str, Any]:
    expected = copy.deepcopy(candidate)
    expected_interface = expected.pop("io", None)
    checks: dict[str, bool] = {
        "id_present": isinstance(detail.get("id"), int) and detail["id"] > 0,
        "name_exact": detail.get("name") == expected_name,
        "team_exact": detail.get("teamId") == team_id,
        "inactive": detail.get("isActive") is False,
        "not_marked_invalid": detail.get("isinvalid") in (None, False),
        "topology_exact": topology(expected) == topology(blueprint),
        "blueprint_exact": json_hash(expected) == json_hash(blueprint),
    }
    if expected_interface is None:
        checks["interface_not_invented"] = interface in (None, {}, {"input": [], "output": []})
    else:
        interface = interface or {}
        inputs = interface.get("input") if isinstance(interface.get("input"), list) else interface.get("input_spec")
        outputs = interface.get("output") if isinstance(interface.get("output"), list) else interface.get("output_spec")
        checks["interface_exact"] = inputs == expected_interface["input_spec"] and outputs == expected_interface["output_spec"]
    failed = [name for name, passed in checks.items() if not passed]
    return {"passed": not failed, "checks": checks, "failed_checks": failed}
