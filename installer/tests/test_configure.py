from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from installer.configure import configure_environment, make_base_url, update_env
from installer.errors import InstallerError


class FakeClient:
    def __init__(self, organizations, teams):
        self.organizations = organizations
        self.teams = teams

    def list_organizations(self):
        return self.organizations

    def list_teams(self, organization_id):
        return [item for item in self.teams if item.get("organizationId") == organization_id]


class ConfigureTests(unittest.TestCase):
    def test_base_url_is_derived_from_zone(self):
        self.assertEqual(make_base_url("EU1"), "https://eu1.make.com/api/v2")
        with self.assertRaises(InstallerError):
            make_base_url("https://eu1.make.com")

    def test_configure_writes_only_discovered_non_secret_values(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text(
                'MAKE_ZONE="eu1"\nMAKE_API_TOKEN="mk"\nNOTION_INSPECT_TOKEN="q7x"\n'
                'MAKE_API_BASE_URL=\nMAKE_ORGANIZATION_ID=\nMAKE_TEAM_ID=\n',
                encoding="utf-8",
            )
            fake = FakeClient(
                [{"id": 22, "name": "Test organization"}],
                [{"id": 11, "name": "Test team", "organizationId": 22}],
            )
            report = configure_environment(env_file, client_factory=lambda base, token: fake)
            text = env_file.read_text(encoding="utf-8")
            self.assertIn('MAKE_API_TOKEN="mk"', text)
            self.assertIn('NOTION_INSPECT_TOKEN="q7x"', text)
            self.assertIn('MAKE_API_BASE_URL="https://eu1.make.com/api/v2"', text)
            self.assertIn('MAKE_ORGANIZATION_ID="22"', text)
            self.assertIn('MAKE_TEAM_ID="11"', text)
            self.assertFalse(report["secrets_written"])
            self.assertNotIn("mk", str(report))
            self.assertNotIn("q7x", str(report))

    def test_multiple_teams_are_selected_by_readable_number(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text('MAKE_ZONE=eu1\nMAKE_API_TOKEN=token\nNOTION_INSPECT_TOKEN=notion\n', encoding="utf-8")
            fake = FakeClient(
                [{"id": 22, "name": "Organization"}],
                [
                    {"id": 10, "name": "Existing", "organizationId": 22},
                    {"id": 11, "name": "Weft test", "organizationId": 22},
                ],
            )
            output = []
            configure_environment(env_file, input_fn=lambda _: "2", output_fn=output.append, client_factory=lambda base, token: fake)
            self.assertIn('MAKE_TEAM_ID="11"', env_file.read_text(encoding="utf-8"))
            self.assertTrue(any("Weft test" in line for line in output))

    def test_missing_private_token_fails_without_modifying_file(self):
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".env"
            env_file.write_text('MAKE_ZONE=eu1\nMAKE_API_TOKEN=\nNOTION_INSPECT_TOKEN=notion\n', encoding="utf-8")
            before = env_file.read_text(encoding="utf-8")
            with self.assertRaises(InstallerError) as caught:
                configure_environment(env_file)
            self.assertEqual(caught.exception.code, "MISSING_CONFIGURATION")
            self.assertEqual(env_file.read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
