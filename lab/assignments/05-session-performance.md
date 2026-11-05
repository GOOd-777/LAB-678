# Лабораторная работа 5. Производительность при увеличении количества сессий

## Цель

Измерить latency, throughput, error rate и задержку SSE при 1, 5, 10, 25 и 50 пользователях.

## Краткая теория

Нагрузка создаётся HTTP-клиентами, не десятком окон Chrome. Locust уже подготовлен, но тесты могут вызывать `/api/join` в цикле.

## Что нужно сделать

Реализовать измерения в `tests/performance/test_session_scalability.py`.

## Как это сделать

1. Для каждого N пользователей создавать сессии через `create_test_session`.
2. Измерять `/api/join`, `/api/action`, `/api/room`.
3. Один SSE-клиент измеряет задержку доставки action.
4. Считать успешные операции в секунду и долю ошибок.
5. Сохранить CSV и графики.

Перед серией вызывайте `reset_room`.

## Инструменты

`requests` / `HttpClient`, `SseClient`, Locust (опционально), matplotlib.

## Какие файлы редактировать

- `tests/performance/test_session_scalability.py`

Locust (не входит в обычный pytest):

```bash
./test_infrastructure/scripts/run_load_test.sh
```

## Рекомендуемые вспомогательные методы

| Метод | Файл | Назначение | Аргументы | Возвращает | Пример |
|---|---|---|---|---|---|
| `create_test_session` | `session_helper.py` | Join | `url`, `name` | dict | `create_test_session(url)` |
| `measure_duration` | `metrics_helper.py` | Latency операции | callable | `(result, ms)` | `measure_duration(lambda: get_room_state(url))` |
| `SseClient` | `event_helper.py` | SSE | `base_url` | клиент | `SseClient(url).start()` |
| `HttpClient` | `network_helper.py` | HTTP | `base_url` | клиент | `HttpClient(url).get('/api/room')` |
| `reset_room` | `session_helper.py` | Очистка | `url` | dict | `reset_room(url)` |
| `plot_session_scalability` | `chart_helper.py` | 4 графика | rows | list[Path] | `plot_session_scalability(rows)` |

## Как запустить тест

```bash
pytest tests/performance/test_session_scalability.py
pytest -m load   # только если реализован необязательный тест на 100 пользователей
```

## Как получить результаты

CSV и PNG в `reports/`, плюс краткие выводы в комментарии или отдельном файле отчёта.

## Как построить график

`plot_session_scalability` строит latency, throughput, error rate и SSE delay.

## Ожидаемый результат

Таблица измерений и графики зависимости от числа пользователей.

## Критерии приёмки

Есть все пять размеров группы, четыре вида метрик и графики. Selenium не используется как генератор нагрузки.

## Дополнительно

100 пользователей (`test_optional_one_hundred_users`).
