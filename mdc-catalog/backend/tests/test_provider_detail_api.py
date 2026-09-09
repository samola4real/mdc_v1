from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.providers.models import Offering, Provider, ProviderCertification


class ProviderLifecycleReadApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.provider = Provider.objects.create(
            provider_id="lifecycle_provider", provider_name="Lifecycle Provider",
            country="Finland", status=Provider.Status.SUSPENDED,
            custom_provider_fields={"sales_region": "Nordics", "nested": ["a", "b"]},
            publication_metadata={"source_type": "curated", "confidence": "curated"},
        )
        ProviderCertification.objects.create(
            provider=cls.provider, code="ISO14001_2015", source_type="public_web",
            confidence="publicly_confirmed", source_note=None,
            source_note_present=True, sequence_index=1,
        )
        ProviderCertification.objects.create(
            provider=cls.provider, code="ISO9001_2015", source_type="provider_confirmed",
            confidence="declared", sequence_index=0,
        )
        cls.second = Offering.objects.create(
            provider=cls.provider, offering_id="lifecycle_provider_shafts",
            offering_name="Precision shafts", service_category="precision_shafts",
            part_family="shaft", support_status=Offering.SupportStatus.UNKNOWN,
            is_active=False, sequence_index=1,
            supported_part_types=[{
                "part_type": "hollow_shaft", "support_status": "unknown",
                "source_type": "not_confirmed", "confidence": "unknown",
            }],
            family_capabilities={"outer_diameter_mm": {"max": None}},
            generic_capabilities={"processes": [{"process": "turning"}, {"process": "milling"}]},
            custom_offering_fields={"commercial_name": "Shaft line"},
            custom_capability_fields={"internal_note": "trusted UI"},
        )
        cls.first = Offering.objects.create(
            provider=cls.provider, offering_id="lifecycle_provider_gears",
            offering_name="Precision gears", service_category="precision_gears",
            part_family="gear", support_status=Offering.SupportStatus.CONFIRMED,
            sequence_index=0,
        )

    def setUp(self):
        self.client = APIClient()

    def test_provider_detail_reads_all_lifecycle_states(self):
        response = self.client.get("/api/providers/lifecycle_provider")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {
            "contract_version": "1.0", "provider_id": "lifecycle_provider",
            "provider_name": "Lifecycle Provider", "country": "Finland",
            "status": "suspended",
            "custom_provider_fields": {"sales_region": "Nordics", "nested": ["a", "b"]},
            "publication_metadata": {"source_type": "curated", "confidence": "curated"},
            "certifications": [
                {"code": "ISO9001_2015", "source_type": "provider_confirmed", "confidence": "declared"},
                {"code": "ISO14001_2015", "source_type": "public_web",
                 "confidence": "publicly_confirmed", "source_note": None},
            ],
            "offerings": [
                {"offering_id": "lifecycle_provider_gears", "offering_name": "Precision gears",
                 "service_category": "precision_gears", "part_family": "gear",
                 "support_status": "confirmed", "is_active": True},
                {"offering_id": "lifecycle_provider_shafts", "offering_name": "Precision shafts",
                 "service_category": "precision_shafts", "part_family": "shaft",
                 "support_status": "unknown", "is_active": False},
            ],
        })

    def test_provider_detail_order_has_stable_tiebreakers(self):
        Offering.objects.update(sequence_index=0)
        ProviderCertification.objects.update(sequence_index=0)
        data = self.client.get("/api/providers/lifecycle_provider").json()
        self.assertEqual([item["offering_id"] for item in data["offerings"]],
                         ["lifecycle_provider_gears", "lifecycle_provider_shafts"])
        self.assertEqual([item["code"] for item in data["certifications"]],
                         ["ISO14001_2015", "ISO9001_2015"])

    def test_unknown_provider_has_safe_stable_404(self):
        response = self.client.get("/api/providers/missing")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["contract_version"], "1.0")
        self.assertEqual(response.json()["error"]["code"], "provider_not_found")
        self.assertNotIn("missing", response.json()["error"]["message"])

    def test_provider_offerings_preserve_order_nested_json_and_custom_fields(self):
        response = self.client.get("/api/providers/lifecycle_provider/offerings")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(data["provider_id"], "lifecycle_provider")
        self.assertEqual([item["offering_id"] for item in data["offerings"]],
                         ["lifecycle_provider_gears", "lifecycle_provider_shafts"])
        inactive = data["offerings"][1]
        self.assertFalse(inactive["is_active"])
        self.assertEqual(inactive["provider_id"], "lifecycle_provider")
        self.assertEqual(inactive["family_capabilities"], {"outer_diameter_mm": {"max": None}})
        self.assertEqual(inactive["generic_capabilities"]["processes"],
                         [{"process": "turning"}, {"process": "milling"}])
        self.assertEqual(inactive["custom_offering_fields"], {"commercial_name": "Shaft line"})
        self.assertEqual(inactive["custom_capability_fields"], {"internal_note": "trusted UI"})

    def test_known_provider_with_zero_offerings_returns_empty_list(self):
        Provider.objects.create(provider_id="empty_provider", provider_name="Empty", country="Finland")
        response = self.client.get("/api/providers/empty_provider/offerings")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["offerings"], [])

    def test_unknown_provider_offerings_returns_404(self):
        response = self.client.get("/api/providers/missing/offerings")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error"]["code"], "provider_not_found")

    def test_offering_detail_preserves_provider_and_capability_fidelity(self):
        response = self.client.get("/api/offerings/lifecycle_provider_shafts")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["contract_version"], "1.0")
        self.assertEqual(data["provider_id"], "lifecycle_provider")
        self.assertFalse(data["is_active"])
        self.assertEqual(data["supported_part_types"], self.second.supported_part_types)
        self.assertEqual(data["family_capabilities"], self.second.family_capabilities)
        self.assertEqual(data["generic_capabilities"], self.second.generic_capabilities)

    def test_unknown_offering_has_safe_stable_404(self):
        response = self.client.get("/api/offerings/missing")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error"]["code"], "offering_not_found")

    def test_read_contracts_do_not_expose_internal_fields(self):
        responses = [
            self.client.get("/api/providers/lifecycle_provider").json(),
            self.client.get("/api/providers/lifecycle_provider/offerings").json(),
            self.client.get("/api/offerings/lifecycle_provider_gears").json(),
        ]
        forbidden = {"id", "created_at", "updated_at", "sequence_index",
                     "provider_publication", "sync_events", "source_note_present"}
        def keys(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    yield key
                    yield from keys(item)
            elif isinstance(value, list):
                for item in value:
                    yield from keys(item)
        for response in responses:
            self.assertFalse(forbidden & set(keys(response)))

    def test_lifecycle_reads_have_bounded_query_counts(self):
        with self.assertNumQueries(3):
            self.client.get("/api/providers/lifecycle_provider")
        with self.assertNumQueries(2):
            self.client.get("/api/providers/lifecycle_provider/offerings")
        with self.assertNumQueries(1):
            self.client.get("/api/offerings/lifecycle_provider_shafts")

    def test_put_and_delete_methods_are_not_added(self):
        self.assertEqual(self.client.put("/api/providers/lifecycle_provider", {}, format="json").status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete("/api/providers/lifecycle_provider").status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.delete("/api/offerings/lifecycle_provider_gears").status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)
