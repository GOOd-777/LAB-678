"""Фикстуры тестового окружения: серверы, Selenium, сессии, mock-источники."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

from test_infrastructure.mock_sources.server import start_mock_server
from tests.helpers.browser_helper import create_driver, quit_driver, show_local_actor
from tests.helpers.metrics_helper import REPORTS, capture_environment
from tests.helpers.page_objects import MotionPage
from tests.helpers.session_helper import cleanup_session, login_via_ui

ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_http(url: str, timeout: float = 8.0) -> None:
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=0.5)
            if response.status_code < 500:
                return
        except requests.RequestException as exc:
            last_error = exc
        time.sleep(0.05)
    raise RuntimeError(f"Server was not ready: {url} ({last_error})")


@pytest.fixture
def free_port() -> int:
    return _free_port()


@pytest.fixture(scope="session")
def reports_dir() -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    capture_environment(project="MotionPlayground_Web")
    return REPORTS


@pytest.fixture(scope="session")
def app_server():
    port = _free_port()
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["MOTION_TEST_MODE"] = "1"
    env["MOTION_USER_TTL"] = "3"
    process = subprocess.Popen(
        [sys.executable, str(ROOT / "room_server.py")],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base_url = f"http://127.0.0.1:{port}"
    try:
        _wait_http(f"{base_url}/api/room")
        yield {"url": base_url, "port": port, "process": process}
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture(scope="session")
def mock_server():
    server, _thread, port = start_mock_server(port=0)
    base_url = f"http://127.0.0.1:{port}"
    _wait_http(f"{base_url}/health")
    try:
        yield {"url": base_url, "port": port, "server": server}
    finally:
        server.shutdown()


@pytest.fixture(scope="session")
def lab_config(app_server, mock_server) -> dict:
    mock = mock_server["url"]
    app = app_server["url"]
    return {
        "catalogs": {
            "backgrounds": f"{mock}/catalogs/backgrounds.json",
            "screensavers": f"{mock}/catalogs/screensavers.json",
            "models": f"{app}/test_assets/manifests/models.json",
        },
        "sources": {
            "local": f"{app}/test_assets/models",
            "http": f"{mock}/local/models",
            "cdn": f"{mock}/cdn/models",
            "delayed": f"{mock}/delayed/models",
            "errors": f"{mock}/errors/models",
        },
        "downloads": {
            "local": f"{mock}/downloads/payload.bin",
            "cdn": f"{mock}/cdn/downloads/payload.bin",
            "delayed": f"{mock}/delayed/downloads/payload.bin?delay_ms=300",
            "throttle": f"{mock}/throttle/downloads/payload.bin?bps=64000",
            "errors": f"{mock}/errors/downloads/payload.bin",
            "incomplete": f"{mock}/incomplete/downloads/payload.bin",
        },
    }


@pytest.fixture
def browser():
    driver = create_driver(headless=True)
    try:
        yield driver
    finally:
        quit_driver(driver)


@pytest.fixture
def animation_page(browser, app_server, lab_config):
    from tests.helpers.model_helper import inject_lab_config

    name = login_via_ui(browser, app_server["url"])
    inject_lab_config(browser, lab_config)
    show_local_actor(browser)
    page = MotionPage(browser, app_server["url"])
    page.user_name = name
    yield page
    cleanup_session(app_server["url"])


@pytest.fixture
def isolated_room(app_server):
    cleanup_session(app_server["url"])
    yield app_server
    cleanup_session(app_server["url"])
