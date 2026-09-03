
from django.test import SimpleTestCase
from rest_framework.test import APIClient

from apps.api.search_serializers import SearchRequestSerializer
from apps.ontology.vocabularies import PART_FAMILIES


class ApiV1FoundationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "maasai-mdc")
        self.assertEqual(response.json()["version"], "v1")

    def test_catalog_filters_endpoint(self):
        response = self.client.get("/api/catalog/filters")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertIn("service_types", data)
        self.assertIn("part_families", data)
        self.assertIn("processes", data)
        self.assertIn("materials", data)
        self.assertIn("material_grades", data)
        self.assertIn("certifications", data)
        self.assertIn("service_discovery", data)
        forbidden_key = "m18" + "_service_discovery"
        self.assertNotIn(forbidden_key, data)

        service_values = {item["value"] for item in data["service_types"]}
        process_values = {item["value"] for item in data["processes"]}
        part_family_values = [item["value"] for item in data["part_families"]]
        legacy_part_family_values = [item["value"] for item in PART_FAMILIES]
        material_grade_values = {item["value"] for item in data["material_grades"]}

        self.assertEqual(part_family_values, legacy_part_family_values)
        self.assertIn("gear_manufacturing", service_values)
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
        self.assertIn("18CrNiMo7-6", material_grade_values)
        self.assertIn("16MnCr5", material_grade_values)
        self.assertIn("20MnCr5", material_grade_values)

        service_discovery = data["service_discovery"]
        self.assertEqual(
            service_discovery["registry_version"],
            "m18_harmonized_v1",
        )
        self.assertIs(service_discovery["search_contract_active"], False)

        profiles = service_discovery["part_type_profiles"]
        self.assertIn("spur_gear", profiles)
        self.assertIn("hollow_shaft", profiles)
        self.assertIn("bracket", profiles)

        spur_gear = profiles["spur_gear"]
        self.assertIn("outside_diameter_mm", spur_gear["family_common_fields"])
        self.assertNotIn("diameter_mm", spur_gear["family_common_fields"])
        self.assertNotIn("diameter_mm", spur_gear["part_type_specific_fields"])
        self.assertNotIn("outer_diameter_mm", spur_gear["family_common_fields"])
        self.assertNotIn("outer_diameter_mm", spur_gear["part_type_specific_fields"])

    def test_harmonized_taxonomy_is_not_active_in_search_serializer(self):
        serializer = SearchRequestSerializer(
            data={
                "part_family": "metal_part",
            }
        )

        self.assertFalse(serializer.is_valid())

    def test_part_type_is_not_active_in_search_serializer(self):
        serializer = SearchRequestSerializer(
            data={
                "part_family": "gear",
                "part_type": "spur_gear",
            }
        )

        self.assertTrue(serializer.is_valid())
        self.assertNotIn("part_type", serializer.validated_data)
