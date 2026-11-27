from copy import deepcopy

from django.test import SimpleTestCase

from apps.api.public_contract import build_public_catalog_filters
from apps.api.service_discovery_search_serializers import ServiceDiscoverySearchRequestSerializer
from apps.ontology.service_discovery_rdf_generator import build_service_discovery_graph
from apps.providers.service_discovery_loaders import load_service_discovery_providers
from apps.search.service_discovery_matching_alignment import search_service_discovery_catalog_via_local_rdf
from tests.test_service_discovery_lenient import canonicalize, payload, search


class CertificationCompletenessTests(SimpleTestCase):
    def test_filter_adds_two_canonical_codes_and_search_accepts_them(self):
        codes = [item["value"] for item in build_public_catalog_filters()["certifications"]]
        self.assertEqual(codes, [
            "ISO9001_2015", "ISO14001_2015", "ISO_TS_16949_partial", "APQP",
            "aerospace_traceability", "full_traceability", "ISO13485_2016", "AS9100_D",
        ])
        for code in codes:
            request = payload({"certifications": [code]})
            canonicalize(request)
        invalid = payload({"certifications": ["EN9100_2018"]})
        invalid.pop("contract_version")
        self.assertFalse(ServiceDiscoverySearchRequestSerializer(data=invalid).is_valid())

    def test_curated_precipart_evidence_is_gear_scoped_in_direct_and_rdf_paths(self):
        records = load_service_discovery_providers()
        precipart = next(record for record in records if record["provider"]["provider_id"] == "precipart")
        self.assertEqual(precipart["provider"]["certifications"], [])
        (offering,) = precipart["offerings"]
        (certification,) = offering["generic_capabilities"]["certifications"]
        self.assertEqual(certification["code"], "AS9100_D")
        self.assertIn("SQS 42929", certification["source_note"])
        sibling = deepcopy(offering)
        sibling["offering_id"] = "fixture_uncertified_sibling"
        sibling["generic_capabilities"]["certifications"] = []
        precipart["offerings"].append(sibling)
        graph = build_service_discovery_graph(records)
        for certs, expected in [
            (["AS9100_D"], ["precipart_precision_gears"]),
            (["ISO13485_2016"], []),
            (["AS9100_D", "ISO9001_2015"], []),
        ]:
            for mode in ("strict", "lenient"):
                data = payload({"certifications": certs}, policy={"discovery_mode": mode})
                self.assertEqual([row["offering_id"] for row in search(data, records)], expected)
                rdf = search_service_discovery_catalog_via_local_rdf(canonicalize(data), graph=graph)
                self.assertEqual([row["offering"]["offering_id"] for row in rdf["results"]], expected)
