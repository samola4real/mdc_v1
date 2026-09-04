from django.test import SimpleTestCase
from rest_framework.test import APIClient

from apps.api.search_serializers import SearchRequestSerializer


class ApiFoundationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "maasai-mdc")
        self.assertEqual(response.json()["contract_version"], "1.0")

    def test_catalog_filters_endpoint(self):
        response = self.client.get("/api/catalog/filters")

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(
            set(data),
            {
                "contract_version",
                "service_categories",
                "part_families",
                "part_types",
                "materials",
                "processes",
                "certifications",
            },
        )

        service_values = {item["value"] for item in data["service_categories"]}
        part_family_values = {item["value"] for item in data["part_families"]}
        process_values = {item["value"] for item in data["processes"]}

        self.assertEqual(
            service_values,
            {"precision_gears", "precision_shafts", "precision_metal_parts"},
        )
        self.assertEqual(part_family_values, {"gear", "shaft", "metal_part"})
        self.assertIn("spur_gear", {item["value"] for item in data["part_types"]["gear"]})
        self.assertIn("hollow_shaft", {item["value"] for item in data["part_types"]["shaft"]})
        self.assertIn("block", {item["value"] for item in data["part_types"]["metal_part"]})
        for process in [
            "machining",
            "hobbing",
            "gear_shaping",
            "deburring",
            "hard_turning",
            "grinding",
            "tooth_grinding",
            "gear_grinding",
            "gear_cutting",
            "surface_grinding",
            "milling",
            "turn_mill",
        ]:
            self.assertIn(process, process_values)

    def test_harmonized_taxonomy_is_not_active_in_legacy_search_serializer(self):
        serializer = SearchRequestSerializer(
            data={
                "part_family": "metal_part",
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_part_type_is_not_active_in_legacy_search_serializer(self):
        serializer = SearchRequestSerializer(
            data={
                "part_family": "gear",
                "part_type": "spur_gear",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertNotIn("part_type", serializer.validated_data)
