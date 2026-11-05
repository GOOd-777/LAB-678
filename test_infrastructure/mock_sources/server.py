#!/usr/bin/env python3
"""Локальный mock-сервер источников моделей, фонов и файлов для скачивания."""

from __future__ import annotations

import json
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "test_assets"
MODELS = ASSETS / "models"
BACKGROUNDS = ASSETS / "backgrounds"
SCREENSAVERS = ASSETS / "screensavers"
DOWNLOADS = ASSETS / "downloads"
MANIFESTS = ASSETS / "manifests"


def _read_bytes(path: Path) -> bytes:
    return path.read_bytes()


def _json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


def _content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".json": "application/json; charset=utf-8",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".bin": "application/octet-stream",
    }.get(suffix, "application/octet-stream")


def _rewrite_catalog(items: list[dict], origin: str) -> list[dict]:
    rewritten = []
    for item in items:
        copy = dict(item)
        url = str(copy.get("url") or "")
        if url.startswith("/"):
            copy["url"] = origin + url
        rewritten.append(copy)
    return rewritten


class MockSourceHandler(BaseHTTPRequestHandler):
    server_version = "MotionMock/1.0"

    def log_message(self, format, *args):
        return

    def _origin(self) -> str:
        host = self.headers.get("Host") or f"127.0.0.1:{self.server.server_port}"
        return f"http://{host}"

    def _send(self, code: int, body: bytes, content_type: str, extra: dict | None = None) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path, extra: dict | None = None, delay_ms: int = 0) -> None:
        if delay_ms:
            time.sleep(delay_ms / 1000.0)
        if not path.is_file():
            self._send(404, _json_bytes({"error": "not_found", "path": str(path.name)}), "application/json")
            return
        self._send(200, _read_bytes(path), _content_type(path), extra)

    def _send_throttled(self, path: Path, bps: int) -> None:
        if not path.is_file():
            self._send(404, b"missing", "text/plain")
            return
        data = _read_bytes(path)
        self.send_response(200)
        self.send_header("Content-Type", _content_type(path))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        chunk = max(1024, bps // 10)
        sent = 0
        while sent < len(data):
            part = data[sent : sent + chunk]
            self.wfile.write(part)
            self.wfile.flush()
            sent += len(part)
            time.sleep(len(part) / max(1, bps))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        delay_ms = int(query.get("delay_ms", ["0"])[0] or 0)
        bps = int(query.get("bps", ["0"])[0] or 0)
        origin = self._origin()

        if path == "/health":
            self._send(200, _json_bytes({"ok": True, "service": "mock-sources"}), "application/json")
            return

        if path == "/catalogs/models.json":
            items = json.loads((MANIFESTS / "models.json").read_text(encoding="utf-8"))
            self._send(200, _json_bytes(items), "application/json")
            return
        if path == "/catalogs/backgrounds.json":
            items = json.loads((MANIFESTS / "backgrounds.json").read_text(encoding="utf-8"))
            self._send(200, _json_bytes(_rewrite_catalog(items, origin)), "application/json")
            return
        if path == "/catalogs/screensavers.json":
            items = json.loads((MANIFESTS / "screensavers.json").read_text(encoding="utf-8"))
            self._send(200, _json_bytes(_rewrite_catalog(items, origin)), "application/json")
            return

        mapping = {
            "/local/models/": MODELS,
            "/cdn/models/": MODELS,
            "/delayed/models/": MODELS,
            "/local/backgrounds/": BACKGROUNDS,
            "/cdn/backgrounds/": BACKGROUNDS,
            "/test_assets/backgrounds/": BACKGROUNDS,
            "/test_assets/screensavers/": SCREENSAVERS,
            "/test_assets/models/": MODELS,
            "/local/screensavers/": SCREENSAVERS,
            "/cdn/screensavers/": SCREENSAVERS,
            "/downloads/": DOWNLOADS,
            "/cdn/downloads/": DOWNLOADS,
            "/delayed/downloads/": DOWNLOADS,
            "/throttle/downloads/": DOWNLOADS,
            "/incomplete/downloads/": DOWNLOADS,
        }

        extra = {}
        if path.startswith("/cdn/"):
            extra = {"X-Cache": "HIT", "CDN-Cache-Control": "public", "Age": "12"}

        if path.startswith("/errors/models/"):
            self._send(500, _json_bytes({"error": "source_unavailable"}), "application/json")
            return
        if path.startswith("/errors/not-found/"):
            self._send(404, _json_bytes({"error": "not_found"}), "application/json")
            return
        if path.startswith("/errors/downloads/"):
            self._send(503, b"service unavailable", "text/plain")
            return

        if path.startswith("/incomplete/downloads/"):
            name = path.rsplit("/", 1)[-1]
            file_path = DOWNLOADS / name
            if not file_path.is_file():
                self._send(404, b"missing", "text/plain")
                return
            data = _read_bytes(file_path)
            half = max(1, len(data) // 2)
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data[:half])
            return

        if path.startswith("/throttle/downloads/"):
            name = path.rsplit("/", 1)[-1]
            self._send_throttled(DOWNLOADS / name, bps or 32_000)
            return

        for prefix, folder in mapping.items():
            if path.startswith(prefix):
                name = path[len(prefix) :]
                if path.startswith("/delayed/"):
                    self._send_file(folder / name, extra, delay_ms=delay_ms or 400)
                else:
                    self._send_file(folder / name, extra, delay_ms=delay_ms)
                return

        self._send(404, _json_bytes({"error": "unknown_path", "path": path}), "application/json")


class ReuseHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def start_mock_server(host: str = "127.0.0.1", port: int = 0):
    server = ReuseHTTPServer((host, port), MockSourceHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    bound = server.server_address[1]
    return server, thread, bound


def wait_until_up(port: int, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                return
        except OSError:
            time.sleep(0.05)
    raise RuntimeError(f"Mock server did not start on {port}")


if __name__ == "__main__":
    chosen = int(os.environ.get("MOCK_PORT", "0"))
    server, _thread, port = start_mock_server(port=chosen)
    print(f"Mock sources: http://127.0.0.1:{port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()
