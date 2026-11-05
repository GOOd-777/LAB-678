"""Locust-сценарии для лабораторной работы 5.

Не запускается вместе со smoke-тестами. Пример:

    locust -f test_infrastructure/load_tests/locustfile.py --headless -u 25 -r 5 -t 30s
"""

from __future__ import annotations

import itertools
import json
import time

from locust import HttpUser, between, events, task

_names = itertools.count(1)


class RoomUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        name = f"locust-{next(_names)}"
        with self.client.post("/api/join", json={"name": name}, catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"join failed: {response.status_code}")
                self.user_id = None
                return
            payload = response.json()
            self.user_id = payload.get("userId")

    @task(3)
    def room(self):
        self.client.get("/api/room", name="/api/room")

    @task(2)
    def action(self):
        if not getattr(self, "user_id", None):
            return
        self.client.post(
            "/api/action",
            json={
                "userId": self.user_id,
                "type": "speed",
                "text": "изменил скорость на x1.0",
                "state": {"speed": 1, "selectedKey": "pulse", "playing": True},
            },
            name="/api/action",
        )

    @task(1)
    def ping(self):
        if not getattr(self, "user_id", None):
            return
        self.client.post("/api/ping", json={"userId": self.user_id}, name="/api/ping")


@events.request.add_listener
def _note_timing(request_type, name, response_time, response_length, exception, **kwargs):
    # Метки времени нужны студентам для сопоставления с SSE.
    if exception:
        return
    _ = (request_type, name, response_time, response_length, time.perf_counter(), json)
