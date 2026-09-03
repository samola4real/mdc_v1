from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json

from django.test import SimpleTestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient


def provider_payload(action="register_provider"):
    return {
        "action": action,
        "provider_id": "demo_gear_provider",
        "provider_name": "Demo Gear Provider Oy",
        "country": "Finland",
        "publication_metadata": {
            "source_type": "provider_confirmed",
            "confidence": "declared",
        },
        "certifications": ["ISO9001_2015"],
        "offerings": [
            {
                "offering_id": "demo_gear_provider_precision_gears",
                "offering_name": "Precision gears",
                "service_category": "precision_gears",
                "part_family": "gear",
                "supported_part_types": ["spur_gear", "helical_gear"],
                "support_status": "confirmed",
                "capabilities": {
                    "module": {"min": 1, "max": 8},
                    "outside_diameter_mm": {"min": 20, "max": 300},
                    "materials": ["alloyed_carburizing_steel"],
                    "available_grades": ["16MnCr5", "20MnCr5"],
                    "processes": ["machining", "hobbing", "gear_grinding"],
                },
            }
        ],
    }


def flexible_register_payload():
    return {
        "action": "register_provider",
        "provider_id": "demo_provider",
        "provider_name": "Demo Provider Oy",
        "country": "Finland",
        "offerings": [
            {
                "offering_id": "demo_provider_steel_services",
                "offering_name": "Steel manufacturing services",
                "custom_offering_fields": [
                    {
                        "name": "Service category",
                        "value": "precision_manufacturing",
                    },
                    {
                        "name": "Capability area",
                        "value": "Steel manufacturing",
                    },
                ],
                "capabilities": {
                    "custom_capability_fields": [
                        {
                            "name": "Maximum thickness",
                            "value": "20",
                            "unit": "mm",
                            "notes": "",
                        },
                        {
                            "name": "Process",
                            "value": "Laser cutting",
                            "unit": "",
                            "notes": "",
                        },
                    ],
                },
            }
        ],
    }


@override_settings(MDC_DEMO_API_ENABLED=True)
class DemoProviderPublicationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_preview_accepts_valid_provider_payload_without_saving(self):
        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=provider_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "valid_demo_preview")
        self.assertFalse(data["mutates_state"])
        self.assertEqual(data["provider"]["provider_id"], "demo_gear_provider")

    def test_preview_rejects_missing_required_fields(self):
        payload = provider_payload()
        payload.pop("provider_id")

        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("provider_id is required", response.json()["errors"][0])

    def test_update_preview_rejects_invalid_controlled_values(self):
        payload = provider_payload("update_existing_provider")
        payload["offerings"][0]["capabilities"]["processes"] = ["magic_cutting"]

        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid value", response.json()["errors"][0])

    def test_register_provider_accepts_custom_offering_fields(self):
        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=flexible_register_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        custom_fields = response.json()["normalized_payload"]["offerings"][0][
            "custom_offering_fields"
        ]
        self.assertIn(
            {"name": "Service category", "value": "precision_manufacturing"},
            custom_fields,
        )

    def test_register_provider_accepts_custom_capability_fields(self):
        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=flexible_register_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        custom_fields = response.json()["normalized_payload"]["offerings"][0][
            "capabilities"
        ]["custom_capability_fields"]
        self.assertIn(
            {
                "name": "Maximum thickness",
                "value": "20",
                "unit": "mm",
                "notes": "",
            },
            custom_fields,
        )

    def test_register_provider_does_not_require_controlled_offering_fields(self):
        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=flexible_register_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offering = response.json()["normalized_payload"]["offerings"][0]
        self.assertIsNone(offering["service_category"])
        self.assertIsNone(offering["part_family"])
        self.assertEqual(offering["supported_part_types"], [])

    def test_register_provider_moves_invalid_service_category_to_custom_field(self):
        payload = provider_payload()
        payload["offerings"][0]["service_category"] = "precision_manufacturing"

        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        offering = data["normalized_payload"]["offerings"][0]
        self.assertIsNone(offering["service_category"])
        self.assertIn(
            {"name": "Service category", "value": "precision_manufacturing"},
            offering["custom_offering_fields"],
        )
        self.assertTrue(
            any("precision_manufacturing" in warning for warning in data["warnings"])
        )

    def test_update_existing_provider_still_rejects_invalid_controlled_values(self):
        payload = provider_payload("update_existing_provider")
        payload["offerings"][0]["service_category"] = "precision_manufacturing"

        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalid value", response.json()["errors"][0])

    def test_route_and_operation_custom_field_names_are_rejected(self):
        payload = flexible_register_payload()
        payload["offerings"][0]["custom_offering_fields"].append(
            {"name": "operation_sequence", "value": "cut then inspect"}
        )

        response = self.client.post(
            "/api/demo/provider-publication/preview",
            data=payload,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not accepted", response.json()["errors"][0])

    def test_simulate_update_writes_demo_state_file(self):
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "provider_demo_state.json"
            with patch("apps.demo.provider_demo_services.STATE_PATH", state_path):
                response = self.client.post(
                    "/api/demo/provider-publication/simulate-update",
                    data=provider_payload("update_existing_provider"),
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertTrue(state_path.exists())
                data = response.json()
                self.assertEqual(
                    data["status"],
                    "existing_provider_update_saved_for_demo",
                )
                self.assertTrue(data["mutates_state"])

    def test_simulate_update_preserves_custom_fields_in_demo_state(self):
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "provider_demo_state.json"
            with patch("apps.demo.provider_demo_services.STATE_PATH", state_path):
                response = self.client.post(
                    "/api/demo/provider-publication/simulate-update",
                    data=flexible_register_payload(),
                    format="json",
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                state = json.loads(state_path.read_text(encoding="utf-8"))
                offering = state["providers"]["demo_provider"]["offerings"][0]
                self.assertIn(
                    {"name": "Service category", "value": "precision_manufacturing"},
                    offering["custom_offering_fields"],
                )
                self.assertIn(
                    {
                        "name": "Process",
                        "value": "Laser cutting",
                        "unit": "",
                        "notes": "",
                    },
                    offering["capabilities"]["custom_capability_fields"],
                )

    def test_provider_state_returns_empty_state_when_file_missing(self):
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "provider_demo_state.json"
            with patch("apps.demo.provider_demo_services.STATE_PATH", state_path):
                response = self.client.get("/api/demo/provider-publication/state")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.json()
                self.assertEqual(data["status"], "demo_provider_state_empty")
                self.assertEqual(data["providers"], {})
                self.assertEqual(data["updates"], {})
                self.assertIsNone(data["last_updated"])
                self.assertFalse(state_path.exists())

    def test_provider_state_returns_saved_providers_and_updates(self):
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "provider_demo_state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "providers": {
                            "demo_provider": {"provider_name": "Demo Provider Oy"}
                        },
                        "updates": {
                            "tasowheel": {"provider_name": "Tasowheel Oy"}
                        },
                        "last_updated": "2026-06-05T10:00:00+00:00",
                    }
                ),
                encoding="utf-8",
            )
            with patch("apps.demo.provider_demo_services.STATE_PATH", state_path):
                response = self.client.get("/api/demo/provider-publication/state")

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.json()
                self.assertEqual(data["status"], "demo_provider_state_loaded")
                self.assertEqual(
                    data["state_path"],
                    "data/demo/provider_demo_state.json",
                )
                self.assertIn("demo_provider", data["providers"])
                self.assertIn("tasowheel", data["updates"])

    def test_provider_state_get_does_not_modify_state_file(self):
        with TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "provider_demo_state.json"
            original = {
                "providers": {"demo_provider": {"provider_name": "Demo Provider Oy"}},
                "updates": {},
                "last_updated": "2026-06-05T10:00:00+00:00",
            }
            state_path.write_text(json.dumps(original, sort_keys=True), encoding="utf-8")
            before = state_path.read_text(encoding="utf-8")

            with patch("apps.demo.provider_demo_services.STATE_PATH", state_path):
                response = self.client.get("/api/demo/provider-publication/state")

            after = state_path.read_text(encoding="utf-8")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(after, before)

    def test_provider_state_endpoint_not_registered_under_shared_api(self):
        response = self.client.get("/api/provider-publication/state")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @override_settings(DEBUG=False, MDC_DEMO_API_ENABLED=False)
    def test_provider_state_respects_demo_disabled_guard(self):
        response = self.client.get("/api/demo/provider-publication/state")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_demo_provider_endpoint_not_registered_under_shared_api(self):
        response = self.client.post(
            "/api/provider-publication/simulate-update",
            data=provider_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
