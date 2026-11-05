"""Smoke-тесты инфраструктуры. Не зависят от студенческих решений."""

from __future__ import annotations

from pathlib import Path

import pytest
import requests

from tests.helpers.chart_helper import plot_demo_chart
from tests.helpers.metrics_helper import calculate_statistics, measure_duration, save_measurements, Measurement
from tests.helpers.network_helper import HttpClient, measure_download
from tests.helpers.session_helper import create_test_session, get_room_state
from tests.helpers.event_helper import SseClient

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.smoke
def test_test_assets_exist():
    models = list((ROOT / "test_assets" / "models").glob("*.json"))
    backgrounds = list((ROOT / "test_assets" / "backgrounds").glob("*"))
    assert models, "Нет тестовых моделей"
    assert backgrounds, "Нет тестовых фонов"


@pytest.mark.smoke
def test_app_server_room_api(app_server):
    room = get_room_state(app_server["url"])
    assert room["multiplayer"] is True
    assert "users" in room


@pytest.mark.smoke
def test_join_and_reset(isolated_room):
    session = create_test_session(isolated_room["url"], "smoke-user")
    assert session["userId"]
    room = get_room_state(isolated_room["url"])
    assert any(user["name"] == "smoke-user" for user in room["users"])


@pytest.mark.smoke
def test_mock_server_health(mock_server):
    response = requests.get(f"{mock_server['url']}/health", timeout=3)
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.smoke
def test_mock_server_serves_model(mock_server):
    response = requests.get(f"{mock_server['url']}/local/models/pulse-circle.json", timeout=3)
    assert response.status_code == 200
    assert response.json()["id"] == "pulse-circle"


@pytest.mark.smoke
def test_selenium_opens_entry_gate(browser, app_server):
    browser.get(app_server["url"])
    assert browser.find_element("id", "entryUserName")
    assert browser.find_element("id", "loadModelBtn")


@pytest.mark.smoke
def test_login_opens_main_app(animation_page):
    assert "сессии" in animation_page.session_badge.lower() or "сессии" in animation_page.session_badge


@pytest.mark.smoke
def test_student_methods_are_not_implemented(animation_page):
    result = animation_page.driver.execute_async_script(
        """
        const done = arguments[0];
        Promise.allSettled([
            window.loadModel('local', 'pulse-circle'),
            window.findBackground('sunset'),
            window.findScreensaver('aurora'),
        ]).then((items) => done(items.map((item) => item.reason && item.reason.message)));
        """
    )
    assert all(message and "Not implemented" in message for message in result)


@pytest.mark.smoke
def test_metrics_and_demo_chart(reports_dir):
    _value, duration = measure_duration(lambda: sum(range(1000)))
    stats = calculate_statistics([duration, duration + 1, duration + 2])
    assert stats["count"] == 3
    path = save_measurements(
        [Measurement(scenario="smoke", duration_ms=duration, extras={"demo": False})],
        "smoke-measurements.csv",
    )
    assert path.exists()
    demo = plot_demo_chart("demo-chart.png")
    assert demo.exists()


@pytest.mark.smoke
def test_sse_snapshot(isolated_room):
    client = SseClient(isolated_room["url"]).start()
    event = client.wait_for(lambda item: item.get("type") == "snapshot")
    client.stop()
    assert event is not None


@pytest.mark.smoke
def test_http_client_and_download(mock_server):
    client = HttpClient(mock_server["url"])
    health = client.get("/health")
    assert health.ok
    sample = measure_download(f"{mock_server['url']}/downloads/payload.bin")
    assert sample["complete"] is True
    assert sample["bytes"] == 256 * 1024
