from django.test import SimpleTestCase

from apps.ontology.service_discovery_registry import get_service_discovery_registry


class ServiceDiscoveryRegistryTests(SimpleTestCase):
    def setUp(self):
        self.registry = get_service_discovery_registry()

    def test_registry_metadata(self):
        self.assertEqual(self.registry["registry_version"], "m18_harmonized_v1")
        self.assertIs(self.registry["search_contract_active"], False)
        forbidden_key = "m18" + "_service_discovery"
        self.assertNotIn(forbidden_key, self.registry)
        self.assertTrue(callable(get_service_discovery_registry))

    def test_service_categories(self):
        categories = {
            item["value"]: item["part_family"]
            for item in self.registry["service_categories"]
        }

        self.assertEqual(
            categories,
            {
                "precision_gears": "gear",
                "precision_shafts": "shaft",
                "precision_metal_parts": "metal_part",
            },
        )

    def test_approved_part_types_exist(self):
        self.assertEqual(
            set(self.registry["part_type_profiles"]),
            {
                "spur_gear",
                "helical_gear",
                "bevel_gear",
                "worm_gear",
                "crown_gear",
                "plain_shaft",
                "stepped_shaft",
                "splined_shaft",
                "worm_shaft",
                "hollow_shaft",
                "block",
                "plate",
                "bracket",
                "bushing",
                "roller",
                "collar",
            },
        )

    def test_corrected_gear_diameter_terminology(self):
        profiles = self.registry["part_type_profiles"]

        for part_type in [
            "spur_gear",
            "helical_gear",
            "bevel_gear",
            "worm_gear",
            "crown_gear",
        ]:
            profile = profiles[part_type]
            self.assertIn("outside_diameter_mm", profile["family_common_fields"])
            self.assertNotIn("diameter_mm", profile["family_common_fields"])
            self.assertNotIn("diameter_mm", profile["part_type_specific_fields"])
            self.assertNotIn("outer_diameter_mm", profile["family_common_fields"])
            self.assertNotIn("outer_diameter_mm", profile["part_type_specific_fields"])

        self.assertEqual(
            profiles["spur_gear"]["part_type_specific_fields"],
            ["face_width_mm"],
        )
        self.assertEqual(
            profiles["helical_gear"]["part_type_specific_fields"],
            ["face_width_mm", "helix_angle_deg"],
        )
        self.assertEqual(
            profiles["bevel_gear"]["part_type_specific_fields"],
            ["face_width_mm", "shaft_angle_deg"],
        )
        self.assertEqual(
            profiles["worm_gear"]["part_type_specific_fields"],
            ["center_distance_mm", "shaft_angle_deg"],
        )
        self.assertEqual(
            profiles["crown_gear"]["part_type_specific_fields"],
            ["face_width_mm", "inner_diameter_mm"],
        )

    def test_shaft_and_metal_part_distinction(self):
        profiles = self.registry["part_type_profiles"]

        hollow_shaft = profiles["hollow_shaft"]
        self.assertIn("outer_diameter_mm", hollow_shaft["family_common_fields"])
        self.assertIn("inner_diameter_mm", hollow_shaft["part_type_specific_fields"])
        self.assertIn("wall_thickness_mm", hollow_shaft["part_type_specific_fields"])

        bracket = profiles["bracket"]
        self.assertEqual(bracket["geometry_class"], "prismatic")
        self.assertIn("bounding_box_mm", bracket["family_common_fields"])
        self.assertIn(
            "vertical_flange_length_mm",
            bracket["part_type_specific_fields"],
        )
        self.assertIn(
            "horizontal_flange_length_mm",
            bracket["part_type_specific_fields"],
        )

        bushing = profiles["bushing"]
        self.assertEqual(bushing["geometry_class"], "rotational")
        self.assertIn("outer_diameter_mm", bushing["family_common_fields"])
        self.assertIn("inner_diameter_mm", bushing["family_common_fields"])
        self.assertIn("flange_diameter_mm", bushing["part_type_specific_fields"])

    def test_generic_fields(self):
        generic_fields = self.registry["generic_requirement_fields"]

        self.assertNotIn("material_grades", generic_fields)

        for profile in self.registry["part_type_profiles"].values():
            self.assertIn("generic_requirement_fields", profile)
            self.assertEqual(profile["generic_requirement_fields"], generic_fields)

    def test_field_definition_completeness_and_semantics(self):
        field_definitions = self.registry["field_definitions"]

        for profile in self.registry["part_type_profiles"].values():
            for field in profile["family_common_fields"]:
                self.assertIn(field, field_definitions)
            for field in profile["part_type_specific_fields"]:
                self.assertIn(field, field_definitions)

        for field in self.registry["generic_requirement_fields"]:
            self.assertIn(field, field_definitions)

        outside_diameter = field_definitions["outside_diameter_mm"]
        self.assertEqual(outside_diameter["scope"], "gear_family")
        self.assertIn("external gears", outside_diameter["note"])
        self.assertIn("Future internal gears", outside_diameter["note"])

        outer_diameter = field_definitions["outer_diameter_mm"]
        self.assertIn("gear outside_diameter_mm", outer_diameter["note"])

        gear_quality = field_definitions["gear_quality"]
        self.assertIn("tolerance_mm", gear_quality["note"])

        center_distance = field_definitions["center_distance_mm"]
        self.assertIn("Mating/interface requirement", center_distance["note"])

        bounding_box = field_definitions["bounding_box_mm"]
        self.assertEqual(
            bounding_box["components"],
            ["length_mm", "width_mm", "height_mm"],
        )
        for component in bounding_box["components"]:
            self.assertIn(component, field_definitions)

        materials = field_definitions["materials"]
        self.assertIn("Material grades are not consumer-selectable", materials["note"])

    def test_registry_is_copy_safe(self):
        first_registry = get_service_discovery_registry()
        first_registry["service_categories"][0]["value"] = "mutated"
        first_registry["part_type_profiles"]["spur_gear"][
            "family_common_fields"
        ].append("mutated")
        first_registry["generic_requirement_fields"].append("material_grades")

        second_registry = get_service_discovery_registry()

        self.assertEqual(
            second_registry["service_categories"][0]["value"],
            "precision_gears",
        )
        self.assertNotIn(
            "mutated",
            second_registry["part_type_profiles"]["spur_gear"][
                "family_common_fields"
            ],
        )
        self.assertNotIn("material_grades", second_registry["generic_requirement_fields"])
