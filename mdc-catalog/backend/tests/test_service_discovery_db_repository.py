from copy import deepcopy
from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase
from rdflib.compare import isomorphic

from apps.ontology.service_discovery_rdf_generator import build_service_discovery_graph
from apps.ontology.service_discovery_rdf_mappings import MDC
from apps.providers.models import (
    CatalogueSyncEvent, Offering, Provider, ProviderCertification, ProviderPublication,
)
from apps.providers.service_discovery_db_repository import (
    ServiceDiscoveryImportError,
    get_service_discovery_provider_from_db,
    import_service_discovery_provider_records,
    load_service_discovery_providers_from_db,
)
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_local_matcher import search_service_discovery_catalog
from tests.test_service_discovery_local_matcher import canonical_request, gear_request, shaft_request


class ServiceDiscoveryDbRepositoryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.records = load_service_discovery_providers()

    def import_records(self):
        return import_service_discovery_provider_records(self.records)

    def test_real_curated_catalogue_exact_parity_and_counts(self):
        original = deepcopy(self.records)
        self.assertEqual(self.import_records(), {"providers": 3, "offerings": 4, "certifications": 5})
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)
        self.assertEqual(self.records, original)
        self.assertEqual(Provider.objects.count(), 3)
        self.assertEqual(Offering.objects.count(), 4)
        self.assertEqual(ProviderCertification.objects.count(), 5)
        self.assertFalse(ProviderPublication.objects.exists())
        self.assertFalse(CatalogueSyncEvent.objects.exists())

    def test_provider_order_independent_of_import_order(self):
        import_service_discovery_provider_records(list(reversed(self.records)))
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)
        self.assertEqual([r["provider"]["provider_id"] for r in self.records],
                         ["demo_machining_provider", "precipart", "tasowheel"])

    def test_certification_and_offering_order_survives_reimport(self):
        self.import_records()
        changed = deepcopy(self.records[-1])
        changed["provider"]["certifications"].reverse()
        changed["offerings"].reverse()
        import_service_discovery_provider_records([changed])
        self.assertEqual(get_service_discovery_provider_from_db("tasowheel"), changed)
        self.assertEqual(list(Offering.objects.filter(provider__provider_id="tasowheel")
                              .order_by("sequence_index").values_list("sequence_index", flat=True)), [0, 1])
        self.assertEqual(list(ProviderCertification.objects.filter(provider__provider_id="tasowheel")
                              .order_by("sequence_index").values_list("sequence_index", flat=True)), [0, 1, 2, 3])

    def test_tied_sequences_have_stable_external_id_tiebreakers(self):
        self.import_records()
        Offering.objects.update(sequence_index=0)
        ProviderCertification.objects.update(sequence_index=0)
        result = get_service_discovery_provider_from_db("tasowheel")
        self.assertEqual([o["offering_id"] for o in result["offerings"]],
                         sorted(o["offering_id"] for o in result["offerings"]))
        self.assertEqual([c["code"] for c in result["provider"]["certifications"]],
                         sorted(c["code"] for c in result["provider"]["certifications"]))

    def test_nested_evidence_nulls_and_list_order(self):
        record = deepcopy(self.records[-1])
        capabilities = record["offerings"][0]["generic_capabilities"]
        capabilities["materials"][0]["available_grades"].reverse()
        capabilities["processes"].reverse()
        record["offerings"][0]["supported_part_types"].reverse()
        record["publication_metadata"]["note"] = {"text": "Tarkkuus – 齿轮", "values": [None, False, 0, 1.25]}
        self.assertIsNone(capabilities["surface_finish_ra_um"]["max"])
        import_service_discovery_provider_records([record])
        self.assertEqual(get_service_discovery_provider_from_db("tasowheel"), record)

    def test_certification_missing_null_empty_and_text_notes_preserved(self):
        record = deepcopy(self.records[-1])
        certifications = record["provider"]["certifications"]
        certifications[1]["source_note"] = None
        certifications[2]["source_note"] = ""
        certifications[3]["source_note"] = "Evidence note"
        import_service_discovery_provider_records([record])
        self.assertEqual(get_service_discovery_provider_from_db("tasowheel"), record)

    def test_idempotency_preserves_counts_and_row_identities(self):
        self.import_records()
        identities = [set(model.objects.values_list("pk", flat=True))
                      for model in (Provider, Offering, ProviderCertification)]
        self.import_records()
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)
        self.assertEqual(identities, [set(model.objects.values_list("pk", flat=True))
                                     for model in (Provider, Offering, ProviderCertification)])

    def test_changed_snapshot_removes_only_its_stale_children(self):
        self.import_records()
        changed = deepcopy(self.records[-1])
        changed["provider"]["display_name"] = "Updated Tasowheel"
        changed["provider"]["country"] = "Sweden"
        changed["provider"]["certifications"] = changed["provider"]["certifications"][:1]
        changed["offerings"] = changed["offerings"][1:]
        changed["publication_metadata"] = {"revision": 2}
        import_service_discovery_provider_records([changed])
        self.assertEqual(load_service_discovery_providers_from_db(), [*self.records[:-1], changed])
        self.assertEqual(Offering.objects.count(), 3)
        self.assertEqual(ProviderCertification.objects.count(), 2)

    def test_empty_snapshot_removes_all_children_but_not_provider(self):
        self.import_records()
        changed = deepcopy(self.records[-1])
        changed["provider"]["certifications"] = []
        changed["offerings"] = []
        import_service_discovery_provider_records([changed])
        self.assertEqual(get_service_discovery_provider_from_db("tasowheel"), changed)
        self.assertEqual(Provider.objects.count(), 3)

    def test_empty_batch_is_noop(self):
        self.import_records()
        self.assertEqual(import_service_discovery_provider_records([]),
                         {"providers": 0, "offerings": 0, "certifications": 0})
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)

    def test_invalid_structure_rejected_before_any_mutation(self):
        invalid_records = [None, {}, {"provider": []}, {"provider": {}, "offerings": []}]
        for field, value in (("provider_id", None), ("display_name", ""), ("country", 123),
                             ("certifications", {}), ("provider_id", "x" * 256)):
            invalid = deepcopy(self.records[0])
            invalid["provider"][field] = value
            invalid_records.append(invalid)
        for field, value in (("offerings", {}), ("publication_metadata", None)):
            invalid = deepcopy(self.records[0])
            invalid[field] = value
            invalid_records.append(invalid)
        for field, value in (("offering_id", ""), ("name", None), ("provider_id", "wrong"),
                             ("supported_part_types", {}), ("family_capabilities", []),
                             ("generic_capabilities", None), ("support_status", "invalid")):
            invalid = deepcopy(self.records[0])
            invalid["offerings"][0][field] = value
            invalid_records.append(invalid)
        for invalid in invalid_records:
            with self.subTest(invalid=invalid), self.assertNumQueries(0):
                with self.assertRaises(ServiceDiscoveryImportError):
                    import_service_discovery_provider_records([self.records[-1], invalid])
        self.assertFalse(Provider.objects.exists())

    def test_unknown_controlled_keys_rejected_without_echoing_payload(self):
        for target in ("root", "provider", "offering", "certification"):
            record = deepcopy(self.records[0])
            destination = {"root": record, "provider": record["provider"],
                           "offering": record["offerings"][0],
                           "certification": record["provider"]["certifications"][0]}[target]
            destination["secret_unknown_key"] = "secret_value"
            with self.subTest(target=target), self.assertRaises(ServiceDiscoveryImportError) as caught:
                import_service_discovery_provider_records([record])
            self.assertNotIn("secret", str(caught.exception))

    def test_duplicate_provider_and_offering_ids_rejected(self):
        duplicate_offering = deepcopy(self.records[0])
        duplicate_offering["offerings"].append(deepcopy(duplicate_offering["offerings"][0]))
        across_provider = deepcopy(self.records[-1])
        across_provider["offerings"][0]["offering_id"] = self.records[0]["offerings"][0]["offering_id"]
        for batch in ([self.records[0], self.records[0]], [duplicate_offering],
                      [self.records[0], across_provider]):
            with self.subTest(batch=batch), self.assertRaises(ServiceDiscoveryImportError):
                import_service_discovery_provider_records(batch)
        self.assertFalse(Provider.objects.exists())

    def test_duplicate_certification_codes_rejected(self):
        record = deepcopy(self.records[0])
        record["provider"]["certifications"] *= 2
        with self.assertRaises(ServiceDiscoveryImportError):
            import_service_discovery_provider_records([record])

    def test_nonportable_json_values_rejected(self):
        for value in (float("nan"), float("inf"), {1: "numeric key"}, {"tuple": (1, 2)}, "bad\x00text"):
            record = deepcopy(self.records[0])
            record["publication_metadata"] = {"invalid": value}
            with self.subTest(value=value), self.assertRaises(ServiceDiscoveryImportError):
                import_service_discovery_provider_records([record])
        self.assertFalse(Provider.objects.exists())

    def test_existing_offering_cannot_move_between_providers_and_batch_rolls_back(self):
        self.import_records()
        records = deepcopy(self.records)
        records[0]["provider"]["display_name"] = "Must roll back"
        records[0]["provider"]["certifications"] = []
        records[0]["offerings"] = []
        # Conflict with an existing offering on a provider processed later.
        records[1]["offerings"][0]["offering_id"] = self.records[-1]["offerings"][0]["offering_id"]
        with self.assertRaisesMessage(ServiceDiscoveryImportError, "belongs to another provider"):
            import_service_discovery_provider_records(records[:2])
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)

    def test_database_failure_rolls_back_new_providers_and_prior_updates(self):
        import_service_discovery_provider_records([self.records[0]])
        changed = deepcopy(self.records)
        changed[0]["provider"]["display_name"] = "Must roll back"
        original = Offering.objects.update_or_create

        def fail_on_second_provider(*args, **kwargs):
            if kwargs["provider"].provider_id == "precipart":
                raise IntegrityError("injected persistence failure")
            return original(*args, **kwargs)

        with patch.object(Offering.objects, "update_or_create", side_effect=fail_on_second_provider):
            with self.assertRaises(IntegrityError):
                import_service_discovery_provider_records(changed)
        self.assertEqual(load_service_discovery_providers_from_db(), [self.records[0]])

    def test_snapshot_cannot_delete_then_reassign_another_providers_identity(self):
        self.import_records()
        records = deepcopy(self.records)
        old_id = records[0]["offerings"][0]["offering_id"]
        records[0]["offerings"] = []
        records[1]["offerings"][0]["offering_id"] = old_id
        with self.assertRaisesMessage(ServiceDiscoveryImportError, "belongs to another provider"):
            import_service_discovery_provider_records(records)
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)

    def test_active_provider_filter_and_missing_detail(self):
        self.import_records()
        for state in (Provider.Status.DRAFT, Provider.Status.SUSPENDED, Provider.Status.ARCHIVED):
            Provider.objects.filter(provider_id="tasowheel").update(status=state)
            with self.subTest(state=state):
                self.assertEqual(load_service_discovery_providers_from_db(), self.records[:-1])
                self.assertIsNone(get_service_discovery_provider_from_db("tasowheel"))
        self.assertIsNone(get_service_discovery_provider_from_db("missing"))

    def test_inactive_offering_filter_and_import_reactivation(self):
        self.import_records()
        Offering.objects.filter(provider__provider_id="tasowheel").update(is_active=False)
        result = get_service_discovery_provider_from_db("tasowheel")
        self.assertEqual(result["offerings"], [])
        Provider.objects.filter(provider_id="tasowheel").update(status=Provider.Status.ARCHIVED)
        self.import_records()
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)

    def test_custom_and_internal_state_not_leaked_or_overwritten(self):
        self.import_records()
        Provider.objects.update(custom_provider_fields={"private": "provider"})
        Offering.objects.update(custom_offering_fields={"private": "offering"},
                                custom_capability_fields={"private": "capability"})
        provider = Provider.objects.get(provider_id="tasowheel")
        publication = ProviderPublication.objects.create(provider=provider, provider_id_snapshot="tasowheel",
                                                         operation="update", submitted_payload={"private": True})
        CatalogueSyncEvent.objects.create(publication=publication, entity_type="provider",
                                           entity_id="tasowheel", operation="upsert")
        self.import_records()
        self.assertEqual(load_service_discovery_providers_from_db(), self.records)
        provider.refresh_from_db()
        self.assertEqual(provider.custom_provider_fields, {"private": "provider"})
        self.assertEqual(Offering.objects.first().custom_offering_fields, {"private": "offering"})
        self.assertEqual(ProviderPublication.objects.count(), 1)
        self.assertEqual(CatalogueSyncEvent.objects.count(), 1)

    def test_catalogue_and_detail_reads_avoid_n_plus_one_queries(self):
        self.import_records()
        with self.assertNumQueries(3):
            self.assertEqual(load_service_discovery_providers_from_db(), self.records)
        with self.assertNumQueries(3):
            self.assertEqual(get_service_discovery_provider_from_db("tasowheel"), self.records[-1])

    def test_optional_containers_have_documented_empty_defaults(self):
        record = deepcopy(self.records[0])
        del record["publication_metadata"]
        del record["provider"]["certifications"]
        for field in ("supported_part_types", "family_capabilities", "part_type_capabilities", "generic_capabilities"):
            del record["offerings"][0][field]
        import_service_discovery_provider_records([record])
        result = get_service_discovery_provider_from_db(record["provider"]["provider_id"])
        self.assertEqual(result["publication_metadata"], {})
        self.assertEqual(result["provider"]["certifications"], [])
        self.assertEqual(result["offerings"][0]["supported_part_types"], [])
        self.assertEqual(result["offerings"][0]["family_capabilities"], {})

    def test_rdf_graph_isomorphism_and_sequence_evidence(self):
        self.import_records()
        yaml_graph = build_service_discovery_graph(provider_records=self.records)
        db_graph = build_service_discovery_graph(provider_records=load_service_discovery_providers_from_db())
        self.assertTrue(isomorphic(yaml_graph, db_graph))
        self.assertEqual(set(yaml_graph), set(db_graph))
        sequences = set(yaml_graph.triples((None, MDC.sequenceIndex, None)))
        self.assertTrue(sequences)
        self.assertEqual(sequences, set(db_graph.triples((None, MDC.sequenceIndex, None))))

    def test_reordered_certification_evidence_rdf_parity(self):
        records = deepcopy(self.records)
        records[-1]["provider"]["certifications"].reverse()
        records[-1]["offerings"].reverse()
        import_service_discovery_provider_records(records)
        self.assertTrue(isomorphic(build_service_discovery_graph(provider_records=records),
                                   build_service_discovery_graph(provider_records=load_service_discovery_providers_from_db())))

    def test_local_matcher_exact_parity_for_families_evidence_and_policies(self):
        self.import_records()
        db_records = load_service_discovery_providers_from_db()
        requests = [
            gear_request("spur_gear"), gear_request("crown_gear"), gear_request("worm_gear"),
            shaft_request("hollow_shaft"), shaft_request("splined_shaft"),
            shaft_request("hollow_shaft", unknown_policy="reject_unknown"),
            gear_request(requirements={"part_family_specifications": {
                "module": {"exact": 2.0}, "diametral_pitch": {"min": 5, "max": 40},
                "outside_diameter_mm": {"exact": 100}, "gear_quality": {"standard": "DIN", "max_class": 5},
            }}),
            gear_request(requirements={"generic_requirements": {"processes": ["hobbing", "turn_mill"]}}),
            canonical_request({"request_id": "metal", "consumer_id": "consumer_001",
                               "service_category": "precision_metal_parts", "part_family": "metal_part",
                               "part_type": "block", "requirements": {}, "match_policy": {}}),
            *[gear_request(requirements={"generic_requirements": {
                "materials": ["steel"], "certifications": ["full_traceability"],
            }}, optional_match_mode=mode) for mode in ("any", "all", "score_only")],
        ]
        seen_providers = set()
        for index, request in enumerate(requests):
            with self.subTest(request=index):
                expected = search_service_discovery_catalog(request, provider_records=self.records)
                actual = search_service_discovery_catalog(request, provider_records=db_records)
                self.assertEqual(actual, expected)
                seen_providers.update(r["provider"]["provider_id"] for r in expected["results"])
        self.assertEqual(seen_providers, {"demo_machining_provider", "precipart", "tasowheel"})
