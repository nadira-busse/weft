#!/usr/bin/env python3
"""Validate Weft schemas, public/regression fixtures, and exported output specs."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:
    print(
        "Missing dependency: jsonschema\n"
        "Install documented dependencies with:\n\n"
        "  python -m pip install -r requirements.txt\n",
        file=sys.stderr,
    )
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "archive_request": ROOT / "schemas/archive-conversation/request.schema.json",
    "archive_response": ROOT / "schemas/archive-conversation/response.schema.json",
    "search_request": ROOT / "schemas/search-archive/request.schema.json",
    "search_response": ROOT / "schemas/search-archive/response.schema.json",
    "context_request": ROOT / "schemas/get-context/request.schema.json",
    "context_response": ROOT / "schemas/get-context/response.schema.json",
}

REGRESSION_TEST_DIRS = {
    "test-1-validation-error",
    "test-2-new-project-new-conversation",
    "test-3-existing-project-new-conversation",
    "test-4-update-existing-conversation",
    "test-5-project-conflict",
    "test-6-missing-project-repair",
    "test-7-missing-project-conflict",
}


@dataclass(frozen=True)
class Target:
    example: Path
    schema_key: str
    valid: bool = True
    semantic_check: Callable[[object], list[str]] | None = None


def example(path: str) -> Path:
    return ROOT / "examples/public-contracts" / path


def regression(path: str) -> Path:
    return ROOT / "regression-tests" / path


TARGETS = [
    Target(example("archive-conversation/request.json"), "archive_request"),
    Target(example("archive-conversation/response.json"), "archive_response"),
    Target(
        example("archive-conversation/validation-error.response.json"),
        "archive_response",
    ),
    Target(
        example("archive-conversation/project-conflict.response.json"),
        "archive_response",
    ),
    Target(
        example("archive-conversation/missing-messages.invalid.json"),
        "archive_request",
        valid=False,
    ),
    Target(
        example("archive-conversation/whitespace-conversation-id.invalid.json"),
        "archive_request",
        valid=False,
    ),
    Target(example("search-archive/query.request.json"), "search_request"),
    Target(example("search-archive/project.request.json"), "search_request"),
    Target(example("search-archive/date.request.json"), "search_request"),
    Target(example("search-archive/response.json"), "search_response"),
    Target(example("search-archive/zero-results.request.json"), "search_request"),
    Target(example("search-archive/zero-results.response.json"), "search_response"),
    Target(example("search-archive/empty.invalid.json"), "search_request", valid=False),
    Target(example("get-context/query.request.json"), "context_request"),
    Target(example("get-context/query.response.json"), "context_response"),
    Target(example("get-context/conversation-id.request.json"), "context_request"),
    Target(example("get-context/conversation-id.response.json"), "context_response"),
    Target(example("get-context/exact-date.request.json"), "context_request"),
    Target(example("get-context/exact-date.response.json"), "context_response"),
    Target(example("get-context/project.request.json"), "context_request"),
    Target(example("get-context/project.response.json"), "context_response"),
    Target(example("get-context/zero-results.response.json"), "context_response"),
    Target(example("get-context/empty.invalid.json"), "context_request", valid=False),
]


def require_equal_context_dates(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["payload is not an object"]
    if payload.get("date_from") != payload.get("date_to"):
        return ["$.date_from and $.date_to must be equal for exact-date retrieval"]
    return []


TARGETS.append(
    Target(
        example("get-context/unequal-dates.invalid.json"),
        "context_request",
        valid=False,
        semantic_check=require_equal_context_dates,
    )
)


BLUEPRINT_OUTPUTS = {
    ROOT / "setup/Make/blueprints/weft_get_context.json": {
        "title": "text",
        "project": "text",
        "full_content": "text",
        "message_count": "number",
        "content_length": "number",
        "conversation_id": "text",
    },
    ROOT / "setup/Make/blueprints/weft_search_archive.json": {
        "id": "text",
        "conversation_id": "text",
        "title": "text",
        "project": "text",
        "summary": "text",
        "key_insights": "text",
        "model_origin": "text",
    },
}


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_json(path: Path) -> object:
    if not path.is_file():
        raise FileNotFoundError(f"missing required file: {relative(path)}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def regression_targets() -> list[Target]:
    targets: list[Target] = []
    invalid_whitespace = regression("test-1-validation-error/request.json")
    for path in sorted((ROOT / "regression-tests").rglob("*.json")):
        payload = load_json(path)
        schema_key = "archive_response" if isinstance(payload, dict) and "status" in payload else "archive_request"
        targets.append(Target(path, schema_key, valid=path != invalid_whitespace))
    return targets


def check_regression_registration() -> list[str]:
    root = ROOT / "regression-tests"
    discovered = {
        path.relative_to(root).parts[0]
        for path in root.rglob("*.json")
    }
    failures = []
    for name in sorted(REGRESSION_TEST_DIRS - discovered):
        failures.append(f"FAIL missing regression test suite: regression-tests/{name}")
    for name in sorted(discovered - REGRESSION_TEST_DIRS):
        failures.append(f"FAIL unregistered regression test suite: regression-tests/{name}")
    if not failures:
        for name in sorted(discovered):
            print(f"OK   regression test suite regression-tests/{name}")
    return failures


def format_error_path(parts: Iterable[object]) -> str:
    rendered = "$"
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def validate_schemas() -> tuple[dict[str, object], list[str]]:
    loaded: dict[str, object] = {}
    failures: list[str] = []
    for key, path in SCHEMAS.items():
        try:
            schema = load_json(path)
            Draft202012Validator.check_schema(schema)
            loaded[key] = schema
            print(f"OK   schema {relative(path)}")
        except Exception as exc:
            failures.append(f"FAIL schema {relative(path)}\n     error: {exc}")
    return loaded, failures


def check_fixture_registration() -> list[str]:
    root = ROOT / "examples/public-contracts"
    discovered = {path for path in root.rglob("*.json")}
    registered = {target.example for target in TARGETS}
    failures = []
    for path in sorted(discovered - registered):
        failures.append(f"FAIL unregistered example: {relative(path)}")
    for path in sorted(registered - discovered):
        failures.append(f"FAIL registered example is missing: {relative(path)}")
    return failures


def validate_target(target: Target, schemas: dict[str, object]) -> list[str]:
    path = target.example
    schema_path = SCHEMAS[target.schema_key]
    try:
        payload = load_json(path)
    except Exception as exc:
        return [f"FAIL fixture {relative(path)}\n     error: {exc}"]

    validator = Draft202012Validator(
        schemas[target.schema_key],
        format_checker=FormatChecker(),
    )
    errors = sorted(validator.iter_errors(payload), key=lambda err: list(err.path))
    messages = [
        f"{format_error_path(error.path)}: {error.message}" for error in errors
    ]
    if target.semantic_check:
        messages.extend(target.semantic_check(payload))

    if target.valid and messages:
        return [
            f"FAIL valid fixture {relative(path)}\n"
            f"     schema: {relative(schema_path)}\n"
            f"     error: {message}"
            for message in messages
        ]
    if not target.valid and not messages:
        return [
            f"FAIL invalid fixture unexpectedly passed: {relative(path)}\n"
            f"     schema: {relative(schema_path)}"
        ]

    expectation = "valid" if target.valid else "expected invalid"
    print(f"OK   {expectation} fixture {relative(path)}")
    return []


def validate_blueprint_outputs() -> list[str]:
    failures: list[str] = []
    for path, expected in BLUEPRINT_OUTPUTS.items():
        try:
            blueprint = load_json(path)
            if not isinstance(blueprint, dict):
                raise TypeError("blueprint root is not an object")
            output_spec = blueprint["io"]["output_spec"]
            results = next(item for item in output_spec if item.get("name") == "results")
            item_spec = results["spec"]["spec"]
            names = [field["name"] for field in item_spec]
            if len(names) != len(set(names)):
                raise ValueError(f"duplicate result fields: {names}")
            actual = {field["name"]: field["type"] for field in item_spec}
            if actual != expected:
                raise ValueError(f"expected {expected}, found {actual}")
            print(f"OK   blueprint output spec {relative(path)}")
        except Exception as exc:
            failures.append(
                f"FAIL blueprint output spec {relative(path)}\n     error: {exc}"
            )
    return failures


def main() -> int:
    schemas, failures = validate_schemas()
    failures.extend(check_fixture_registration())
    failures.extend(check_regression_registration())

    if len(schemas) == len(SCHEMAS):
        for target in TARGETS:
            failures.extend(validate_target(target, schemas))
        for target in regression_targets():
            failures.extend(validate_target(target, schemas))

    failures.extend(validate_blueprint_outputs())

    if failures:
        print("\n\n".join(failures), file=sys.stderr)
        return 1

    print("\nAll schemas, public/regression fixtures, invalid fixtures, and blueprint outputs passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
