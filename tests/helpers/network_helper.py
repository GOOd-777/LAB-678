"""HTTP-клиент, измерение скачивания и пропускной способности."""

from __future__ import annotations

import time
from typing import Any

import requests

from tests.helpers.metrics_helper import Measurement, measure_duration


class HttpClient:
    def __init__(self, base_url: str = "", timeout: float = 8.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}{path}"

    def get(self, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(self.url(path), **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(self.url(path), **kwargs)


def measure_download(
    url: str,
    timeout: float = 10.0,
    expected_bytes: int | None = None,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    client = session or requests.Session()
    started = time.perf_counter()
    try:
        response = client.get(url, timeout=timeout, stream=True)
        chunks: list[bytes] = []
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                chunks.append(chunk)
        body = b"".join(chunks)
        duration_ms = (time.perf_counter() - started) * 1000.0
        declared = response.headers.get("Content-Length")
        complete = True
        if declared is not None:
            complete = len(body) == int(declared)
        if expected_bytes is not None:
            complete = complete and len(body) == expected_bytes
        status = "ok" if response.ok and complete else "incomplete" if response.ok else f"http_{response.status_code}"
        return {
            "status_code": response.status_code,
            "bytes": len(body),
            "duration_ms": duration_ms,
            "complete": complete,
            "status": status,
            "headers": dict(response.headers),
        }
    except requests.Timeout:
        return {
            "status_code": 0,
            "bytes": 0,
            "duration_ms": (time.perf_counter() - started) * 1000.0,
            "complete": False,
            "status": "timeout",
            "headers": {},
        }
    except requests.exceptions.ChunkedEncodingError:
        return {
            "status_code": 200,
            "bytes": 0,
            "duration_ms": (time.perf_counter() - started) * 1000.0,
            "complete": False,
            "status": "incomplete",
            "headers": {},
        }
    except requests.RequestException as exc:
        name = exc.__class__.__name__
        status = "incomplete" if "Chunked" in name or "Connection" in name else f"error:{name}"
        return {
            "status_code": 0,
            "bytes": 0,
            "duration_ms": (time.perf_counter() - started) * 1000.0,
            "complete": False,
            "status": status,
            "headers": {},
        }


def calculate_throughput(byte_count: int, duration_ms: float) -> float:
    seconds = max(duration_ms / 1000.0, 1e-9)
    return byte_count / seconds


def download_measurement(url: str, scenario: str, source: str, repetition: int = 1, **kwargs) -> Measurement:
    sample = measure_download(url, **kwargs)
    extras = {
        "bytes": sample["bytes"],
        "complete": sample["complete"],
        "status_code": sample["status_code"],
    }
    if sample["complete"] and sample["duration_ms"] > 0:
        extras["throughput_bps"] = calculate_throughput(sample["bytes"], sample["duration_ms"])
    return Measurement(
        scenario=scenario,
        source=source,
        repetition=repetition,
        duration_ms=sample["duration_ms"],
        status=sample["status"],
        extras=extras,
    )


def measure_http_latency(operation) -> tuple[Any, float]:
    return measure_duration(operation)
