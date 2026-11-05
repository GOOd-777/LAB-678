"""Инфраструктурные проверки HTTP API комнаты."""

from __future__ import annotations

import pytest
import requests

from tests.helpers.session_helper import create_test_session, post_action


@pytest.mark.api
@pytest.mark.smoke
def test_join_requires_name(app_server):
    response = requests.post(f"{app_server['url']}/api/join", json={"name": ""}, timeout=5)
    assert response.status_code == 400


@pytest.mark.api
@pytest.mark.smoke
def test_action_updates_feed(isolated_room):
    session = create_test_session(isolated_room["url"], "api-user")
    payload = post_action(isolated_room["url"], session["userId"], "start", "запустил анимацию")
    assert payload["ok"] is True
    assert payload["entry"]["type"] == "start"
