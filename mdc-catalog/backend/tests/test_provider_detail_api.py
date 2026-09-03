from django.test import SimpleTestCase
from rest_framework.test import APIClient


class ProviderDetailApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_tasowheel_provider_detail(self):
        response = self.client.get("/api/providers/tasowheel")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["provider_id"], "tasowheel")
        self.assertEqual(data["display_name"], "Tasowheel Oy")
        self.assertEqual(data["country"], "Finland")
        self.assertIn("offerings", data)

        offering_ids = {offering["offering_id"] for offering in data["offerings"]}
        self.assertIn("tasowheel_gears_shafts_precision", offering_ids)

    def test_get_unknown_provider_returns_404(self):
        response = self.client.get("/api/providers/unknown_provider")

        self.assertEqual(response.status_code, 404)

        data = response.json()

        self.assertEqual(data["error"]["code"], "not_found")

    def test_get_tasowheel_offering_detail(self):
        response = self.client.get(
            "/api/offerings/tasowheel_gears_shafts_precision"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
            data["offering_id"],
            "tasowheel_gears_shafts_precision",
        )
        self.assertEqual(data["provider_id"], "tasowheel")
        self.assertEqual(data["service_type"], "gear_manufacturing")
        self.assertIn("capabilities", data)
        self.assertIn("diameter_mm", data["capabilities"])

    def test_get_unknown_offering_returns_404(self):
        response = self.client.get("/api/offerings/unknown_offering")

        self.assertEqual(response.status_code, 404)

        data = response.json()

        self.assertEqual(data["error"]["code"], "not_found")

    def test_get_demo_provider_detail(self):
        response = self.client.get("/api/providers/demo_machining_provider")

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["provider_id"], "demo_machining_provider")
        self.assertEqual(data["display_name"], "Demo Machining Provider")

    def test_get_demo_offering_detail(self):
        response = self.client.get(
            "/api/offerings/demo_machining_provider_precision_machining"
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(
            data["offering_id"],
            "demo_machining_provider_precision_machining",
        )
        self.assertEqual(data["service_type"], "machining")