import base64
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rdflib import Graph, Literal, URIRef

from apps.providers.catalogue_sync_service import (
    CatalogueSyncConfigurationError,
    replace_service_discovery_graph_in_fuseki,
)


class _Response:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@override_settings(
    SERVICE_DISCOVERY_FUSEKI_GRAPH_STORE_ENDPOINT="http://example.invalid/mdc/data?default",
    FUSEKI_SYNC_TIMEOUT_SECONDS=2,
)
class P33FusekiWriteAuthenticationTests(SimpleTestCase):
    def graph(self):
        graph = Graph()
        graph.add((URIRef("urn:test:s"), URIRef("urn:test:p"), Literal("v")))
        return graph

    @override_settings(
        SERVICE_DISCOVERY_FUSEKI_USERNAME="admin",
        SERVICE_DISCOVERY_FUSEKI_PASSWORD="secret-value",
    )
    def test_basic_authorization_header_is_added_without_changing_payload(self):
        captured = {}
        expected_graph = self.graph()

        def fake_urlopen(request, timeout):
            captured["authorization"] = request.get_header("Authorization")
            captured["content_type"] = request.get_header("Content-type")
            captured["method"] = request.get_method()
            captured["body"] = request.data
            captured["timeout"] = timeout
            return _Response()

        with patch("apps.providers.catalogue_sync_service.urlopen", side_effect=fake_urlopen):
            replace_service_discovery_graph_in_fuseki(expected_graph)

        expected = base64.b64encode(b"admin:secret-value").decode("ascii")
        self.assertEqual(captured["authorization"], f"Basic {expected}")
        self.assertEqual(captured["method"], "PUT")
        self.assertIn("text/turtle", captured["content_type"])
        actual_graph = Graph()
        actual_graph.parse(data=captured["body"].decode("utf-8"), format="turtle")
        self.assertEqual(set(actual_graph), set(expected_graph))
        self.assertEqual(captured["timeout"], 2)

    @override_settings(
        SERVICE_DISCOVERY_FUSEKI_USERNAME="",
        SERVICE_DISCOVERY_FUSEKI_PASSWORD="",
    )
    def test_no_authorization_header_when_credentials_are_not_configured(self):
        captured = {}

        def fake_urlopen(request, timeout):
            captured["authorization"] = request.get_header("Authorization")
            return _Response()

        with patch("apps.providers.catalogue_sync_service.urlopen", side_effect=fake_urlopen):
            replace_service_discovery_graph_in_fuseki(self.graph())

        self.assertIsNone(captured["authorization"])

    @override_settings(
        SERVICE_DISCOVERY_FUSEKI_USERNAME="admin",
        SERVICE_DISCOVERY_FUSEKI_PASSWORD="",
    )
    def test_username_without_password_is_rejected_before_http(self):
        with patch("apps.providers.catalogue_sync_service.urlopen") as urlopen_mock:
            with self.assertRaises(CatalogueSyncConfigurationError):
                replace_service_discovery_graph_in_fuseki(self.graph())
        urlopen_mock.assert_not_called()

    @override_settings(
        SERVICE_DISCOVERY_FUSEKI_USERNAME="",
        SERVICE_DISCOVERY_FUSEKI_PASSWORD="secret-value",
    )
    def test_password_without_username_is_rejected_before_http(self):
        with patch("apps.providers.catalogue_sync_service.urlopen") as urlopen_mock:
            with self.assertRaises(CatalogueSyncConfigurationError):
                replace_service_discovery_graph_in_fuseki(self.graph())
        urlopen_mock.assert_not_called()
