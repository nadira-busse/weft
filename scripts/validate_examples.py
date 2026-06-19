#!/usr/bin/env python3
"""
Validate public example payloads against their JSON Schemas.

This script validates only the public contract examples.
It does not validate private Make payloads, Notion records, internal mappings,
or production runtime data.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError:
    print(
        "Missing dependency: jsonschema\n"
        "Install it with:\n\n"
        "  py -m pip install jsonschema\n",
        file=sys.stderr,
    )
    sys.exit(2)


ROOT = Path(__file__).resolve().parents[1]


SCHEMA_FILES = [
    ROOT / "schemas/archive/conversation-archive-request.schema.json",
    ROOT / "schemas/archive/conversation-archive-response.schema.json",
    ROOT / "schemas/archive/message.schema.json",
    ROOT / "schemas/search/search-archive-request.schema.json",
    ROOT / "schemas/search/search-archive-response.schema.json",
    ROOT / "schemas/context/get-context-request.schema.json",
    ROOT / "schemas/context/get-context-response.schema.json",
]


VALIDATION_TARGETS = [
    (
        "archive_conversation request",
        ROOT / "examples/public-contracts/archive-conversation/request.example.json",
        ROOT / "schemas/archive/conversation-archive-request.schema.json",
    ),
    (
        "archive_conversation response",
        ROOT / "examples/public-contracts/archive-conversation/response.example.json",
        ROOT / "schemas/archive/conversation-archive-response.schema.json",
    ),
    (
        "search_archive request",
        ROOT / "examples/public-contracts/search-archive/request.example.json",
        ROOT / "schemas/search/search-archive-request.schema.json",
    ),
    (
        "search_archive response",
        ROOT / "examples/public-contracts/search-archive/response.example.json",
        ROOT / "schemas/search/search-archive-response.schema.json",
    ),
    (
        "get_context request",
        ROOT / "examples/public-contracts/get-context/request.example.json",
        ROOT / "schemas/context/get-context-request.schema.json",
    ),
    (
        "get_context response",
        ROOT / "examples/public-contracts/get-context/response.example.json",
        ROOT / "schemas/context/get-context-response.schema.json",
    ),
]


def load_json(path: Path) -> object:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path.relative_to(ROOT)}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def build_schema_registry() -> Registry:
    registry = Registry()

    for schema_path in SCHEMA_FILES:
        schema = load_json(schema_path)

        if not isinstance(schema, dict):
            raise ValueError(f"Schema is not a JSON object: {schema_path.relative_to(ROOT)}")

        schema_id = schema.get("$id")

        if not isinstance(schema_id, str) or not schema_id:
            raise ValueError(f"Schema is missing $id: {schema_path.relative_to(ROOT)}")

        resource = Resource.from_contents(schema)
        registry = registry.with_resource(schema_id, resource)

    return registry


def format_error_path(path_parts: Iterable[object]) -> str:
    parts = list(path_parts)

    if not parts:
        return "$"

    rendered = "$"

    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        else:
            rendered += f".{part}"

    return rendered


def validate_example(
    label: str,
    example_path: Path,
    schema_path: Path,
    registry: Registry,
) -> list[str]:
    example = load_json(example_path)
    schema = load_json(schema_path)

    validator = Draft202012Validator(schema, registry=registry)
    errors = sorted(validator.iter_errors(example), key=lambda error: list(error.path))

    if not errors:
        print(f"OK   {label}")
        return []

    messages = []

    for error in errors:
        path = format_error_path(error.path)
        messages.append(
            f"FAIL {label}\n"
            f"     example: {example_path.relative_to(ROOT)}\n"
            f"     schema:  {schema_path.relative_to(ROOT)}\n"
            f"     path:    {path}\n"
            f"     error:   {error.message}"
        )

    return messages


def main() -> int:
    all_errors: list[str] = []

    try:
        registry = build_schema_registry()
    except Exception as exc:
        print(f"FAIL schema registry\n     error: {exc}", file=sys.stderr)
        return 1

    for label, example_path, schema_path in VALIDATION_TARGETS:
        try:
            all_errors.extend(validate_example(label, example_path, schema_path, registry))
        except Exception as exc:
            all_errors.append(f"FAIL {label}\n     error: {exc}")

    if all_errors:
        print("\n\n".join(all_errors), file=sys.stderr)
        return 1

    print("\nAll public examples match their schemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())