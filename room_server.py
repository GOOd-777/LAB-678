#!/usr/bin/env python3
"""Статический сайт + совместная комната (SSE + REST, только stdlib)."""

from __future__ import annotations

import json
import os
import queue
import socket
import threading
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(os.environ.get("PORT", "8080"))
MAX_FEED = 120
USER_TTL = float(os.environ.get("MOTION_USER_TTL", "90"))
TEST_MODE = os.environ.get("MOTION_TEST_MODE") == "1"

DEFAULT_STATE = {
    "selectedKey": "pulse",
    "speed": 1,
    "use3d": False,
    "combine": False,
    "playing": True,
    "modelRotX": -18,
    "modelRotY": 28,
    "theme": "neon",
}

lock = threading.Lock()
users: dict[str, dict] = {}
feed: list[dict] = []
sse_clients: list[queue.Queue] = []
request_log: list[dict] = []
MAX_REQUEST_LOG = 500


def local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def prune_users() -> None:
    now = time.time()
    stale = [uid for uid, u in users.items() if now - u["lastSeen"] > USER_TTL]
    for uid in stale:
        name = users[uid]["name"]
        del users[uid]
        push_feed(uid, name, "leave", f"{name} отключился")


def snapshot() -> dict:
    prune_users()
    return {
        "multiplayer": True,
        "users": [
            {
                "id": uid,
                "name": u["name"],
                "color": u["color"],
                "state": u.get("state", dict(DEFAULT_STATE)),
            }
            for uid, u in users.items()
        ],
        "feed": feed[-MAX_FEED:],
    }


def push_feed(user_id: str, user_name: str, action_type: str, text: str) -> dict:
    entry = {
        "id": str(uuid.uuid4()),
        "ts": int(time.time() * 1000),
        "userId": user_id,
        "userName": user_name,
        "type": action_type,
        "text": text,
    }
    feed.append(entry)
    if len(feed) > MAX_FEED:
        del feed[: len(feed) - MAX_FEED]
    return entry


def broadcast(message: dict) -> None:
    data = json.dumps(message, ensure_ascii=False)
    dead: list[queue.Queue] = []
    for q in sse_clients:
        try:
            q.put_nowait(data)
        except queue.Full:
            dead.append(q)
    for q in dead:
        if q in sse_clients:
            sse_clients.remove(q)


USER_COLORS = ["#22d3ee", "#a78bfa", "#34d399", "#fbbf24", "#f472b6", "#60a5fa", "#fb7185"]


def pick_color() -> str:
    used = {u["color"] for u in users.values()}
    for color in USER_COLORS:
        if color not in used:
            return color
    return USER_COLORS[len(users) % len(USER_COLORS)]


class RoomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, format, *args):
        if TEST_MODE:
            request_log.append(
                {
                    "ts": int(time.time() * 1000),
                    "message": format % args if args else str(format),
                }
            )
            if len(request_log) > MAX_REQUEST_LOG:
                del request_log[: len(request_log) - MAX_REQUEST_LOG]
        if args and isinstance(args[0], str) and args[0].startswith("GET /api/"):
            return
        super().log_message(format, *args)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/room":
            self._json_response(snapshot())
            return
        if path == "/api/events":
            self._sse_stream()
            return
        if TEST_MODE and path == "/api/test/logs":
            with lock:
                payload = {
                    "ok": True,
                    "feed": list(feed),
                    "requestLog": list(request_log),
                    "users": snapshot()["users"],
                    "sseClients": len(sse_clients),
                }
            self._json_response(payload)
            return
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        body = self._read_json()
        if path == "/api/join":
            self._handle_join(body)
            return
        if path == "/api/ping":
            self._handle_ping(body)
            return
        if path == "/api/action":
            self._handle_action(body)
            return
        if TEST_MODE and path == "/api/test/reset":
            self._handle_test_reset()
            return
        self.send_error(404)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _json_response(self, payload: dict, code: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _sse_stream(self) -> None:
        client_q: queue.Queue = queue.Queue(maxsize=200)
        with lock:
            sse_clients.append(client_q)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        def send_obj(obj: dict) -> bool:
            try:
                line = f"data: {json.dumps(obj, ensure_ascii=False)}\n\n".encode("utf-8")
                self.wfile.write(line)
                self.wfile.flush()
                return True
            except (BrokenPipeError, ConnectionResetError, OSError):
                return False

        if not send_obj({"type": "snapshot", **snapshot()}):
            with lock:
                if client_q in sse_clients:
                    sse_clients.remove(client_q)
            return

        try:
            while True:
                try:
                    payload = client_q.get(timeout=25)
                    if not send_obj(json.loads(payload)):
                        break
                except queue.Empty:
                    if not send_obj({"type": "ping"}):
                        break
        finally:
            with lock:
                if client_q in sse_clients:
                    sse_clients.remove(client_q)

    def _handle_join(self, body: dict) -> None:
        name = str(body.get("name", "")).strip()[:32]
        if not name:
            self._json_response({"ok": False, "error": "name_required"}, 400)
            return
        user_id = str(uuid.uuid4())
        with lock:
            users[user_id] = {
                "name": name,
                "color": pick_color(),
                "lastSeen": time.time(),
                # У каждого подключившегося своё состояние объекта/анимации.
                # Оно не синхронизируется с другими пользователями.
                "state": dict(DEFAULT_STATE),
            }
            entry = push_feed(user_id, name, "join", f"{name} подключился")
            snap = snapshot()
        broadcast({"type": "feed", "entry": entry, "users": snap["users"]})
        self._json_response({"userId": user_id, "userName": name, "state": users[user_id]["state"], **snap})

    def _handle_ping(self, body: dict) -> None:
        user_id = str(body.get("userId", ""))
        with lock:
            if user_id in users:
                users[user_id]["lastSeen"] = time.time()
        self._json_response({"ok": True})

    def _handle_action(self, body: dict) -> None:
        user_id = str(body.get("userId", ""))
        action_type = str(body.get("type", "unknown"))
        text = str(body.get("text", "")).strip()[:240]
        patch = body.get("state")
        if not text:
            self._json_response({"ok": False, "error": "empty text"}, 400)
            return

        with lock:
            if user_id not in users:
                self._json_response({"ok": False, "error": "unknown user"}, 403)
                return
            users[user_id]["lastSeen"] = time.time()
            user_name = users[user_id]["name"]
            if isinstance(patch, dict):
                # Сохраняем состояние только для автора действия.
                # Остальным клиентам оно не отправляется, чтобы их объекты оставались независимыми.
                user_state = users[user_id].setdefault("state", dict(DEFAULT_STATE))
                for key in DEFAULT_STATE:
                    if key in patch:
                        user_state[key] = patch[key]
            entry = push_feed(user_id, user_name, action_type, text)
            snap = snapshot()

        broadcast(
            {
                "type": "action",
                "entry": entry,
                "users": snap["users"],
            }
        )
        self._json_response({"ok": True, "entry": entry})

    def _handle_test_reset(self) -> None:
        with lock:
            users.clear()
            feed.clear()
            request_log.clear()
        self._json_response({"ok": True, "reset": True})


class ReuseHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def main() -> None:
    ip = local_ip()
    try:
        server = ReuseHTTPServer(("0.0.0.0", PORT), RoomHandler)
    except OSError as err:
        if err.errno == 48:
            print(f"Ошибка: порт {PORT} уже занят.")
            print("Выполните: ./stop-server.sh")
            print("или закройте другое окно терминала с сервером.")
            raise SystemExit(1) from err
        raise

    print("Motion Playground — совместный режим")
    print(f"  На этом компьютере:  http://127.0.0.1:{PORT}")
    print(f"  В локальной сети:    http://{ip}:{PORT}")
    print("  Остановка: Ctrl+C")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен.")


if __name__ == "__main__":
    main()
