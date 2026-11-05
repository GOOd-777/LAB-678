"""Создание пользователей и сессий через HTTP API и UI."""

from __future__ import annotations

import itertools
import time
from typing import Any

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from tests.helpers.browser_helper import js, wait_clickable, wait_for_condition, wait_visible

_counter = itertools.count(1)


def create_test_user(prefix: str = "student") -> str:
    return f"{prefix}-{next(_counter)}-{int(time.time() * 1000) % 100000}"


def create_test_session(base_url: str, name: str | None = None) -> dict[str, Any]:
    user_name = name or create_test_user()
    response = requests.post(f"{base_url}/api/join", json={"name": user_name}, timeout=5)
    response.raise_for_status()
    payload = response.json()
    payload["name"] = user_name
    return payload


def get_room_state(base_url: str) -> dict[str, Any]:
    response = requests.get(f"{base_url}/api/room", timeout=5)
    response.raise_for_status()
    return response.json()


def post_action(base_url: str, user_id: str, action_type: str, text: str, state: dict | None = None) -> dict:
    response = requests.post(
        f"{base_url}/api/action",
        json={"userId": user_id, "type": action_type, "text": text, "state": state or {}},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def reset_room(base_url: str) -> dict:
    response = requests.post(f"{base_url}/api/test/reset", json={}, timeout=5)
    response.raise_for_status()
    return response.json()


def get_server_logs(base_url: str) -> dict:
    response = requests.get(f"{base_url}/api/test/logs", timeout=5)
    response.raise_for_status()
    return response.json()


def login_via_ui(driver: WebDriver, base_url: str, name: str | None = None) -> str:
    user_name = name or create_test_user("ui")
    driver.get(base_url)
    wait_visible(driver, By.ID, "entryUserName")
    field = driver.find_element(By.ID, "entryUserName")
    field.clear()
    field.send_keys(user_name)
    wait_clickable(driver, By.ID, "entryConnectBtn").click()
    wait_for_condition(
        driver,
        lambda d: js(d, "return document.body.classList.contains('session-active')"),
        timeout=10,
    )
    return user_name


def cleanup_session(base_url: str) -> None:
    try:
        reset_room(base_url)
    except requests.RequestException:
        pass
