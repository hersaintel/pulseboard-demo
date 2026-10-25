import json
import threading
import unittest
from http.client import HTTPConnection
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from server import create_server


class PulseboardServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path):
        connection = HTTPConnection("127.0.0.1", self.port, timeout=2)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        headers = {key.lower(): value for key, value in response.getheaders()}
        connection.close()
        return response.status, headers, body

    def test_health_endpoint_reports_service_status(self):
        status, headers, body = self.request("/api/health")
        payload = json.loads(body)

        self.assertEqual(status, 200)
        self.assertEqual(headers["content-type"], "application/json; charset=utf-8")
        self.assertEqual(payload, {"service": "pulseboard-api", "status": "ok"})

    def test_metrics_endpoint_returns_dashboard_data(self):
        status, _, body = self.request("/api/metrics")
        payload = json.loads(body)

        self.assertEqual(status, 200)
        self.assertEqual(payload["summary"]["uptime"], "99.98%")
        self.assertEqual(len(payload["services"]), 3)
        self.assertEqual(payload["services"][0]["status"], "Operational")

    def test_frontend_is_served_from_root(self):
        status, headers, body = self.request("/")

        self.assertEqual(status, 200)
        self.assertTrue(headers["content-type"].startswith("text/html"))
        self.assertIn(b"Pulseboard", body)

    def test_unknown_api_route_returns_json_404(self):
        status, headers, body = self.request("/api/unknown")
        payload = json.loads(body)

        self.assertEqual(status, 404)
        self.assertEqual(headers["content-type"], "application/json; charset=utf-8")
        self.assertEqual(payload["error"], "Not found")


if __name__ == "__main__":
    unittest.main()
