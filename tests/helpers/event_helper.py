"""Сбор SSE, серверных логов и сопоставление событий."""

from __future__ import annotations

import json
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Any

from selenium.webdriver.remote.webdriver import WebDriver

from tests.helpers.browser_helper import js
from tests.helpers.session_helper import get_room_state, get_server_logs

EVENT_CATALOG = [
    {"event": "Подключение", "ui": True, "sse": True, "server": True, "contract": True},
    {"event": "Отключение", "ui": True, "sse": True, "server": True, "contract": True, "note": "появляется после TTL"},
    {"event": "Запуск анимации", "ui": True, "sse": True, "server": True, "contract": True},
    {"event": "Остановка", "ui": True, "sse": True, "server": True, "contract": True},
    {"event": "Изменение скорости", "ui": True, "sse": True, "server": True, "contract": True},
    {"event": "Изменение эффекта", "ui": True, "sse": True, "server": True, "contract": True},
    {"event": "Переключение 2D/3D", "ui": True, "sse": True, "server": True, "contract": True},
    {"event": "Ошибка загрузки модели", "ui": True, "sse": False, "server": False, "contract": False},
    {"event": "Потеря SSE", "ui": True, "sse": False, "server": False, "contract": False},
    {"event": "Повторное подключение", "ui": True, "sse": True, "server": True, "contract": True, "note": "новый join"},
    {"event": "Неуспешный HTTP-запрос", "ui": False, "sse": False, "server": False, "contract": False},
]


@dataclass
class SseClient:
    base_url: str
    events: list[dict] = field(default_factory=list)
    _stop: threading.Event = field(default_factory=threading.Event)
    _thread: threading.Thread | None = None

    def start(self) -> "SseClient":
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        deadline = time.time() + 8
        while time.time() < deadline and not self.events:
            time.sleep(0.05)
        return self

    def _run(self) -> None:
        request = urllib.request.Request(
            f"{self.base_url}/api/events",
            headers={"Accept": "text/event-stream", "Cache-Control": "no-cache"},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                buffer = ""
                while not self._stop.is_set():
                    line = response.readline()
                    if not line:
                        break
                    text = line.decode("utf-8", errors="replace").rstrip("\r\n")
                    if text.startswith("data:"):
                        buffer += text[5:].lstrip()
                    elif text == "" and buffer:
                        try:
                            payload = json.loads(buffer)
                            payload["_received_ts"] = time.time() * 1000.0
                            self.events.append(payload)
                        except json.JSONDecodeError:
                            pass
                        buffer = ""
        except Exception as exc:  # noqa: BLE001
            self.events.append({"type": "client_error", "error": str(exc)})

    def wait_for(self, predicate, timeout: float = 5.0) -> dict | None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            for event in self.events:
                if predicate(event):
                    return event
            time.sleep(0.05)
        return None

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)


def collect_sse_events(base_url: str, duration: float = 1.0) -> list[dict]:
    client = SseClient(base_url).start()
    time.sleep(duration)
    events = list(client.events)
    client.stop()
    return events


def collect_browser_events(driver: WebDriver) -> list[dict]:
    return js(driver, "return window.motionBrowserEvents || [];") or []


def collect_ui_feed(driver: WebDriver) -> list[str]:
    return js(
        driver,
        """
        return Array.from(document.querySelectorAll('#activityFeed .feed-item')).map((el) => el.textContent);
        """,
    )


def match_events(expected_types: list[str], feed: list[dict]) -> dict[str, bool]:
    present = {entry.get("type") for entry in feed}
    return {event_type: event_type in present for event_type in expected_types}


def collect_server_feed(base_url: str) -> list[dict]:
    room = get_room_state(base_url)
    return room.get("feed") or []


def collect_all_event_sources(base_url: str, driver: WebDriver | None = None) -> dict[str, Any]:
    payload = {
        "feed": collect_server_feed(base_url),
        "logs": get_server_logs(base_url),
        "browser": collect_browser_events(driver) if driver else [],
        "ui": collect_ui_feed(driver) if driver else [],
    }
    return payload
