# События Motion Playground

## Что уже есть в системе

Сервер хранит ленту `feed` в памяти и рассылает её по SSE.

| Тип | Когда появляется | UI | SSE | Серверные логи / feed |
|---|---|---|---|---|
| `join` | `POST /api/join` | да | да (`feed`) | да |
| `leave` | пользователь не активен дольше TTL | да, после появления | да | да |
| `start` / `animation` | Старт или выбор эффекта | да | да (`action`) | да |
| `stop` | Стоп | да | да | да |
| `speed` | изменение `#speed` | да | да | да |
| `combine` | чекбокс комбинации | да | да | да |
| `mode` | переключение 2D/3D | да | да | да |
| `theme` | смена темы | да | да | да |
| `model_rotate` | поворот 3D-куба | да | да | да |
| `snapshot` | новое SSE-подключение | нет | да | нет в feed |
| `ping` | keep-alive SSE | нет | да | нет в feed |

## Где смотреть

- UI: `#activityFeed .feed-item`.
- SSE: `GET /api/events`.
- HTTP-снимок: `GET /api/room` → поле `feed`.
- В тестовом режиме: `GET /api/test/logs`.

## Чего нет в контракте

Эти события можно наблюдать в UI или в браузере, но сервер их не регистрирует. Это не дефект, если в задании не требуется добавлять новый контракт.

- Ошибка загрузки модели (`motion:model-load-error`, `#modelLoadError`).
- Потеря SSE: клиент показывает «Соединение потеряно», отдельного серверного события нет.
- Неуспешный HTTP-запрос (`400` на пустое имя и т.п.) не попадает в `feed`.
- Мгновенное отключение вкладки логируется как `leave` только после TTL (в тестах TTL = 3 с).

## Как проверять

```python
from tests.helpers.event_helper import SseClient, collect_server_feed, collect_browser_events, EVENT_CATALOG

feed = collect_server_feed(app_server["url"])
client = SseClient(app_server["url"]).start()
event = client.wait_for(lambda item: item.get("type") == "action")
```

Таблица `EVENT_CATALOG` — исходный перечень для лабораторной 6. Заполните колонку «Обнаружено» по факту.
