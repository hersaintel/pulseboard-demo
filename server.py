#!/usr/bin/env python3
"""Pulseboard: a zero-dependency status dashboard and JSON API."""

from __future__ import annotations

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = ROOT / "public"

METRICS = {
    "summary": {
        "uptime": "99.98%",
        "requests": "1.24M",
        "latency": "84 ms",
        "incidents": 0,
    },
    "services": [
        {"name": "Public API", "status": "Operational", "latency": "76 ms"},
        {"name": "Web Application", "status": "Operational", "latency": "91 ms"},
        {"name": "Background Jobs", "status": "Operational", "latency": "85 ms"},
    ],
    "traffic": [42, 55, 48, 68, 61, 74, 70, 82, 78, 91, 86, 96],
}


class PulseboardHandler(SimpleHTTPRequestHandler):
    """Serve the dashboard assets and read-only API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def log_message(self, format_string, *args):
        print(f"[pulseboard] {self.address_string()} - {format_string % args}")

    def send_json(self, payload, status=200):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            self.send_json({"service": "pulseboard-api", "status": "ok"})
            return
        if path == "/api/metrics":
            self.send_json(METRICS)
            return
        if path.startswith("/api/"):
            self.send_json({"error": "Not found", "path": path}, status=404)
            return
        super().do_GET()


def create_server(host="127.0.0.1", port=8000):
    return ThreadingHTTPServer((host, port), PulseboardHandler)


def main():
    parser = argparse.ArgumentParser(description="Run the Pulseboard demo server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()

    server = create_server(args.host, args.port)
    print(f"Pulseboard running at http://{args.host}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Pulseboard")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
