from copy import deepcopy

from django.test import SimpleTestCase

from apps.providers.exceptions import SeedDataError
from apps.providers.loaders import load_catalog_seed_data
from apps.providers.providers_utils import (
    get_provider_seed_file_path,
    list_provider_seed_files,
)
from apps.providers.services import (
    OfferingNotFoundError,
    ProviderNotFoundError,
    clear_seed_cache,
    get_offering_by_id,
    get_offerings_for_provider,
    get_provider_by_id,
)
from apps.providers.validators import validate_seed_data



class ProviderSeedDataTests(SimpleTestCase):
    def setUp(self):
        clear_seed_cache()

    def test_seed_data_loads(self):
        data = load_catalog_seed_data()

        self.assertIn("metadata", data)
        self.assertIn("providers", data)
        self.assertIn("offerings", data)

    def test_route_fields_are_not_included(self):
        data = load_catalog_seed_data()

        self.assertFalse(data["metadata"]["route_fields_included"])

        forbidden_keys = {
            "routes",
            "route_steps",
            "operation_sequence",
            "machine_sequence",
            "process_order",
            "subcontractor_route",
            "cycle_time",
            "setup_time",
            "machine_availability",
            "pricing",
            "capacity_calendar",
        }

        for offering in data["offerings"]:
            self.assertTrue(forbidden_keys.isdisjoint(offering.keys()))

    def test_get_provider_by_id_returns_tasowheel(self):
        provider = get_provider_by_id("tasowheel")

        self.assertEqual(provider["provider_id"], "tasowheel")
        self.assertEqual(provider["display_name"], "Tasowheel Oy")
        self.assertEqual(provider["country"], "Finland")

    def test_get_provider_by_id_raises_for_unknown_provider(self):
        with self.assertRaises(ProviderNotFoundError):
            get_provider_by_id("unknown_provider")

    def test_get_offering_by_id_returns_primary_tasowheel_offering(self):
        offering = get_offering_by_id("tasowheel_gears_shafts_precision")

        self.assertEqual(
            offering["offering_id"],
            "tasowheel_gears_shafts_precision",
        )
        self.assertEqual(offering["provider_id"], "tasowheel")
        self.assertEqual(offering["service_type"], "gear_manufacturing")

    def test_get_offering_by_id_raises_for_unknown_offering(self):
        with self.assertRaises(OfferingNotFoundError):
            get_offering_by_id("unknown_offering")

    def test_get_offerings_for_provider_returns_tasowheel_offering(self):
        offerings = get_offerings_for_provider("tasowheel")

        self.assertEqual(len(offerings), 1)
        self.assertEqual(
            offerings[0]["offering_id"],
            "tasowheel_gears_shafts_precision",
        )

    def test_tsw_material_grades_are_present(self):
        offering = get_offering_by_id("tasowheel_gears_shafts_precision")

        self.assertIn("18CrNiMo7-6", offering["supported_material_grades"])
        self.assertIn("16MnCr5", offering["supported_material_grades"])
        self.assertIn("20MnCr5", offering["supported_material_grades"])

    def test_unknown_fields_remain_unknown(self):
        offering = get_offering_by_id("tasowheel_gears_shafts_precision")
        capabilities = offering["capabilities"]

        self.assertIsNone(capabilities["surface_finish_ra_um"]["max"])
        self.assertEqual(
            capabilities["surface_finish_ra_um"]["confidence"],
            "unknown",
        )

        self.assertIsNone(capabilities["tolerance_mm"]["min"])
        self.assertEqual(
            capabilities["tolerance_mm"]["confidence"],
            "unknown",
        )

    def test_provider_seed_folder_contains_tasowheel_file(self):
        seed_file = get_provider_seed_file_path("tasowheel")

        self.assertTrue(seed_file.exists())

    def test_list_provider_seed_files_includes_tasowheel(self):
        seed_files = list_provider_seed_files()
        seed_file_names = {path.name for path in seed_files}

        self.assertIn("tasowheel.yaml", seed_file_names)

    def test_load_catalog_seed_data_uses_merged_catalog(self):
        data = load_catalog_seed_data()

        self.assertEqual(data["metadata"]["dataset_id"], "catalog_seed_v1")
        self.assertFalse(data["metadata"]["route_fields_included"])
        self.assertIn("tasowheel_seed_v1", data["metadata"]["source_dataset_ids"])

        provider_ids = {provider["provider_id"] for provider in data["providers"]}
        offering_ids = {offering["offering_id"] for offering in data["offerings"]}

        self.assertIn("tasowheel", provider_ids)
        self.assertIn("tasowheel_gears_shafts_precision", offering_ids)

    def test_duplicate_provider_ids_are_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        duplicate_provider = deepcopy(data["providers"][0])
        data["providers"].append(duplicate_provider)

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Duplicate provider_id", str(context.exception))

    def test_duplicate_offering_ids_are_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        duplicate_offering = deepcopy(data["offerings"][0])
        data["offerings"].append(duplicate_offering)

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Duplicate offering_id", str(context.exception))
    
    

    def test_invalid_service_type_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["offerings"][0]["service_type"] = "unknown_service"

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Invalid value", str(context.exception))
        self.assertIn("service_type", str(context.exception))

    def test_invalid_part_family_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["offerings"][0]["part_families"].append("unknown_part_family")

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Invalid value", str(context.exception))
        self.assertIn("part_families", str(context.exception))

    def test_invalid_process_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["offerings"][0]["processes"].append("magic_cutting")

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Invalid value", str(context.exception))
        self.assertIn("processes", str(context.exception))

    def test_invalid_supported_material_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["offerings"][0]["supported_materials"].append(
            {
                "material": "unobtainium",
                "confidence": "declared",
                "source_type": "provider_confirmed",
            }
        )

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("references unknown material", str(context.exception))
        self.assertIn("unobtainium", str(context.exception))

    def test_undeclared_material_grade_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["offerings"][0]["supported_material_grades"].append(
            "UNDECLARED_TEST_GRADE"
        )

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("unsupported material grade", str(context.exception))
    
    def test_invalid_certification_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["providers"][0]["certifications"].append(
            {
                "code": "UNKNOWN_CERT",
                "label": "Unknown certification",
                "confidence": "declared",
                "source_type": "provider_confirmed",
            }
        )

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Invalid value", str(context.exception))
        self.assertIn("certifications", str(context.exception))

    def test_invalid_quality_standard_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["offerings"][0]["capabilities"]["quality"]["standard"] = (
            "UNKNOWN_STANDARD"
        )

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Invalid value", str(context.exception))
        self.assertIn("quality.standard", str(context.exception))


    def test_catalog_loads_multiple_providers(self):
        data = load_catalog_seed_data()

        provider_ids = {provider["provider_id"] for provider in data["providers"]}

        self.assertIn("tasowheel", provider_ids)
        self.assertIn("demo_machining_provider", provider_ids)
        self.assertIn("demo_heat_treatment_provider", provider_ids)

    def test_catalog_loads_multiple_offerings(self):
        data = load_catalog_seed_data()

        offering_ids = {offering["offering_id"] for offering in data["offerings"]}

        self.assertIn("tasowheel_gears_shafts_precision", offering_ids)
        self.assertIn(
            "demo_machining_provider_precision_machining",
            offering_ids,
        )
        self.assertIn(
            "demo_heat_treatment_provider_heat_treatment",
            offering_ids,
        )

    def test_get_provider_by_id_returns_demo_machining_provider(self):
        provider = get_provider_by_id("demo_machining_provider")

        self.assertEqual(provider["provider_id"], "demo_machining_provider")
        self.assertEqual(provider["display_name"], "Demo Machining Provider")
        self.assertEqual(provider["country"], "Finland")

    def test_get_provider_by_id_returns_demo_heat_treatment_provider(self):
        provider = get_provider_by_id("demo_heat_treatment_provider")

        self.assertEqual(provider["provider_id"], "demo_heat_treatment_provider")
        self.assertEqual(provider["display_name"], "Demo Heat Treatment Provider")
        self.assertEqual(provider["country"], "Finland")

    def test_get_offerings_for_demo_machining_provider(self):
        offerings = get_offerings_for_provider("demo_machining_provider")

        self.assertEqual(len(offerings), 1)
        self.assertEqual(
            offerings[0]["offering_id"],
            "demo_machining_provider_precision_machining",
        )
        self.assertEqual(offerings[0]["service_type"], "machining")

    def test_get_offerings_for_demo_heat_treatment_provider(self):
        offerings = get_offerings_for_provider("demo_heat_treatment_provider")

        self.assertEqual(len(offerings), 1)
        self.assertEqual(
            offerings[0]["offering_id"],
            "demo_heat_treatment_provider_heat_treatment",
        )
        self.assertEqual(offerings[0]["service_type"], "heat_treatment")



    def test_material_grade_with_unknown_material_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["material_grades"].append(
            {
                "grade_id": "TEST_GRADE_UNKNOWN_MATERIAL",
                "label": "Test grade with unknown material",
                "material_id": "unknown_material",
                "confidence": "curated",
                "source_type": "curated",
            }
        )

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("unknown material_id", str(context.exception))


    def test_offering_with_unknown_supported_material_is_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        data["offerings"][0]["supported_materials"].append(
            {
                "material": "unknown_material",
                "confidence": "curated",
                "source_type": "curated",
            }
        )

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("references unknown material", str(context.exception))

    def test_duplicate_material_grade_ids_are_rejected(self):
        data = deepcopy(load_catalog_seed_data())

        duplicate_grade = deepcopy(data["material_grades"][0])
        data["material_grades"].append(duplicate_grade)

        with self.assertRaises(SeedDataError) as context:
            validate_seed_data(data)

        self.assertIn("Duplicate material grade_id", str(context.exception))

    def test_demo_material_grades_are_loaded(self):
        data = load_catalog_seed_data()

        grade_ids = {grade["grade_id"] for grade in data["material_grades"]}

        self.assertIn("42CrMo4", grade_ids)
        self.assertIn("Al6082", grade_ids)