"""Small Make and Notion clients with bounded, explicit retry behavior."""

from __future__ import annotations

import json
import ssl
import time
from dataclasses import dataclass
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .errors import InstallerError


def safe_error(payload: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key.casefold() in {"code", "message", "name", "type", "status", "detail"} and isinstance(child, (str, int, float, bool, type(None))):
                    result[key] = child
                elif isinstance(child, (dict, list)):
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(payload)
    return result or {"message": "The service returned no report-safe error details."}


@dataclass(frozen=True)
class AmbiguousMutationError(RuntimeError):
    method: str
    path: str


class MakeClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        opener: Callable[..., Any] = urlopen,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.opener = opener
        self.sleeper = sleeper
        self.mutation_count = 0
        self.request_log: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        write: bool = False,
        body: dict[str, Any] | None = None,
        allow_statuses: set[int] | None = None,
    ) -> Any:
        method = method.upper()
        token = self.token
        data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8") if body is not None else None
        mutation = method in {"POST", "PUT", "PATCH", "DELETE"}
        if mutation:
            self.mutation_count += 1
        attempts = 0
        while True:
            attempts += 1
            request = Request(
                f"{self.base_url}{path}",
                data=data,
                method=method,
                headers={
                    "Authorization": f"Token {token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "User-Agent": "weft-public-installer/1.0",
                },
            )
            try:
                with self.opener(request, timeout=60, context=ssl.create_default_context()) as response:
                    raw = response.read()
                    payload = json.loads(raw.decode("utf-8")) if raw else {}
                    self.request_log.append({"method": method, "path": path.split("?", 1)[0], "status": response.status, "mutation": mutation})
                    return payload
            except HTTPError as exc:
                raw = exc.read()
                try:
                    payload = json.loads(raw.decode("utf-8")) if raw else {}
                except (UnicodeDecodeError, json.JSONDecodeError):
                    payload = {}
                self.request_log.append({"method": method, "path": path.split("?", 1)[0], "status": exc.code, "mutation": method != "GET"})
                if allow_statuses and exc.code in allow_statuses:
                    return {}
                retry_after = exc.headers.get("Retry-After") if exc.headers else None
                if method == "GET" and exc.code == 429 and attempts < 4:
                    try:
                        delay = min(max(float(retry_after or 1), 0), 30)
                    except ValueError:
                        delay = 1
                    self.sleeper(delay)
                    continue
                if mutation and exc.code >= 500:
                    raise AmbiguousMutationError(method, path) from None
                raise InstallerError(
                    f"Make {method} {path.split('?', 1)[0]} failed: {safe_error(payload)}",
                    code="MAKE_API_ERROR",
                    action="Correct the reported API or permission issue, then rerun with the same state file.",
                    retry_safe=method == "GET" or exc.code < 500,
                ) from None
            except (URLError, TimeoutError):
                self.request_log.append({"method": method, "path": path.split("?", 1)[0], "status": None, "mutation": method != "GET"})
                if method != "GET":
                    raise AmbiguousMutationError(method, path) from None
                if attempts < 4:
                    self.sleeper(min(2 ** (attempts - 1), 8))
                    continue
                raise InstallerError(
                    f"Make GET {path.split('?', 1)[0]} failed before a response was received",
                    code="MAKE_CONNECTIVITY_ERROR",
                    action="Restore connectivity and rerun preflight.",
                    retry_safe=True,
                ) from None

    @staticmethod
    def unwrap_list(payload: Any, key: str) -> list[dict[str, Any]]:
        if isinstance(payload, dict) and isinstance(payload.get(key), list):
            return [item for item in payload[key] if isinstance(item, dict)]
        if isinstance(payload, dict) and isinstance(payload.get("response"), dict):
            return MakeClient.unwrap_list(payload["response"], key)
        return []

    @staticmethod
    def unwrap_record(payload: Any, key: str) -> dict[str, Any]:
        if isinstance(payload, dict) and isinstance(payload.get(key), dict):
            return payload[key]
        if isinstance(payload, dict) and isinstance(payload.get("response"), dict):
            return MakeClient.unwrap_record(payload["response"], key)
        return payload if isinstance(payload, dict) else {}


    def list_organizations(self) -> list[dict[str, Any]]:
        return self.unwrap_list(self.request("GET", "/organizations?pg[limit]=1000"), "organizations")

    def list_teams(self, organization_id: int) -> list[dict[str, Any]]:
        query = urlencode({"organizationId": organization_id, "pg[limit]": 1000})
        return self.unwrap_list(self.request("GET", f"/teams?{query}"), "teams")

    def list_scenarios(self, team_id: int) -> list[dict[str, Any]]:
        query = urlencode({"teamId": team_id, "pg[limit]": 10000})
        return self.unwrap_list(self.request("GET", f"/scenarios?{query}"), "scenarios")

    def list_connections(self, team_id: int) -> list[dict[str, Any]]:
        query = urlencode({"teamId": team_id, "pg[limit]": 10000})
        records: list[dict[str, Any]] = []
        for item in self.unwrap_list(self.request("GET", f"/connections?{query}"), "connections"):
            connection_id = item.get("id")
            if not isinstance(connection_id, int):
                raise InstallerError("Make returned a connection without an integer ID", code="MAKE_READBACK_INVALID")
            detail = self.unwrap_record(self.request("GET", f"/connections/{connection_id}"), "connection")
            merged = {**item, **detail}
            allowed = ("id", "name", "accountName", "accountLabel", "accountType", "packageName", "teamId", "organizationId", "scoped", "editable")
            records.append({key: merged[key] for key in allowed if key in merged})
        return records

    def list_data_structures(self, team_id: int) -> list[dict[str, Any]]:
        query = urlencode({"teamId": team_id, "pg[limit]": 10000})
        records: list[dict[str, Any]] = []
        for item in self.unwrap_list(self.request("GET", f"/data-structures?{query}"), "dataStructures"):
            structure_id = item.get("id")
            if not isinstance(structure_id, int):
                raise InstallerError("Make returned a Data Structure without an integer ID", code="MAKE_READBACK_INVALID")
            detail = self.unwrap_record(self.request("GET", f"/data-structures/{structure_id}"), "dataStructure")
            merged = {**item, **detail}
            records.append({key: merged[key] for key in ("id", "name", "teamId", "strict", "spec") if key in merged})
        return records

    def create_data_structure(self, body: dict[str, Any]) -> dict[str, Any]:
        payload = self.request("POST", "/data-structures", write=True, body=body)
        return self.unwrap_record(payload, "dataStructure")

    def get_data_structure(self, structure_id: int) -> dict[str, Any]:
        return self.unwrap_record(self.request("GET", f"/data-structures/{structure_id}"), "dataStructure")

    def create_scenario(self, body: dict[str, Any]) -> dict[str, Any]:
        payload = self.request("POST", "/scenarios?confirmed=true", write=True, body=body)
        return self.unwrap_record(payload, "scenario")

    def get_scenario(self, scenario_id: int) -> dict[str, Any]:
        return self.unwrap_record(self.request("GET", f"/scenarios/{scenario_id}"), "scenario")

    def get_scenario_blueprint(self, scenario_id: int) -> Any:
        return self.request("GET", f"/scenarios/{scenario_id}/blueprint?draft=false")

    def get_scenario_interface(self, scenario_id: int) -> dict[str, Any]:
        return self.unwrap_record(self.request("GET", f"/scenarios/{scenario_id}/interface", allow_statuses={404}), "interface")

    def stop_scenario(self, scenario_id: int) -> None:
        self.request("POST", f"/scenarios/{scenario_id}/stop", write=True)


class NotionClient:
    VERSION = "2026-03-11"

    def __init__(self, token: str, *, opener: Callable[..., Any] = urlopen) -> None:
        self.token = token
        self.opener = opener
        self.mutation_count = 0
        self.request_log: list[dict[str, Any]] = []

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        method = method.upper()
        if method not in {"GET", "POST"} or (method == "POST" and path != "/v1/search"):
            raise InstallerError("The installer permits only read-only Notion operations", code="CLIENT_SAFETY_ERROR")
        request = Request(
            f"https://api.notion.com{path}",
            data=json.dumps(body, separators=(",", ":")).encode("utf-8") if body is not None else None,
            method=method,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Notion-Version": self.VERSION,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "weft-public-installer/1.0",
            },
        )
        try:
            with self.opener(request, timeout=60, context=ssl.create_default_context()) as response:
                raw = response.read()
                self.request_log.append({"method": method, "path": path, "status": response.status, "write": False})
                return json.loads(raw.decode("utf-8")) if raw else {}
        except HTTPError as exc:
            raw = exc.read()
            try:
                payload = json.loads(raw.decode("utf-8")) if raw else {}
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = {}
            raise InstallerError(
                f"Notion {method} {path} failed: {safe_error(payload)}",
                code="NOTION_API_ERROR",
                action="Confirm the token and integration access, then rerun preflight.",
                retry_safe=True,
            ) from None
        except (URLError, TimeoutError):
            raise InstallerError(
                f"Notion {method} {path} failed before a response was received",
                code="NOTION_CONNECTIVITY_ERROR",
                action="Restore connectivity and rerun preflight.",
                retry_safe=True,
            ) from None

    @staticmethod
    def title(record: dict[str, Any]) -> str:
        title = record.get("title")
        if isinstance(title, list):
            return "".join(str(item.get("plain_text") or "") for item in title if isinstance(item, dict))
        return str(title or "")

    def discover_resources(self, requested: list[dict[str, str]]) -> dict[str, Any]:
        resources: dict[str, Any] = {}
        for item in requested:
            key, title = item["key"], item["title"]
            search = self.request("POST", "/v1/search", {"query": title, "page_size": 100})
            matches = [
                record
                for record in search.get("results", [])
                if isinstance(record, dict)
                and record.get("object") == "data_source"
                and self.title(record).casefold() == title.casefold()
            ]
            if len(matches) != 1:
                candidates = [{"id": record.get("id"), "title": self.title(record)} for record in matches]
                raise InstallerError(
                    f"Expected exactly one Notion data source named {title!r}; found {len(matches)}",
                    code="NOTION_RESOURCE_AMBIGUOUS" if matches else "NOTION_RESOURCE_MISSING",
                    resource_type="notion_data_source",
                    candidates=candidates,
                    config_key="NOTION_INSPECT_TOKEN",
                    action="Share the exact duplicated Weft database with the integration and remove or rename ambiguous duplicates.",
                    retry_safe=True,
                )
            data_source_id = str(matches[0].get("id") or "")
            data_source = self.request("GET", f"/v1/data_sources/{data_source_id}")
            parent = data_source.get("parent") if isinstance(data_source.get("parent"), dict) else matches[0].get("parent", {})
            database_id = str((parent or {}).get("database_id") or "")
            if not database_id:
                raise InstallerError(f"Notion data source {title!r} has no parent database", code="NOTION_RESOURCE_INVALID")
            self.request("GET", f"/v1/databases/{database_id}")
            properties: dict[str, Any] = {}
            for name, prop in (data_source.get("properties") or {}).items():
                if isinstance(prop, dict):
                    prop_type = str(prop.get("type") or "")
                    properties[name] = {
                        "id": prop.get("id"),
                        "type": prop_type,
                        "configuration": prop.get(prop_type) if isinstance(prop.get(prop_type), (dict, list)) else {},
                    }
            resources[key] = {
                "title": self.title(data_source) or title,
                "database_id": database_id,
                "data_source_id": data_source_id,
                "properties": properties,
            }
        return resources
