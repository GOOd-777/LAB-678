# Лабораторная работа 8. Скорость скачивания из разных источников

## Цель

Сравнить загрузку одного и того же 256 КБ файла из локального HTTP, mock CDN, источника с задержкой и источника с ограничением скорости.

## Краткая теория

Файл `payload.bin` одинаков во всех источниках. Загрузка успешна только если тело получено целиком. Timeout и HTTP-ошибка — отдельные статусы.

## Что нужно сделать

Реализовать тесты в `tests/performance/test_download_sources.py`.

## Как это сделать

1. URL взять из `lab_config["downloads"]`.
2. Измерить `measure_download` / `download_measurement`.
3. Проверить error, timeout и incomplete.
4. Сравнить первый запрос и повторный (тёплый кеш на стороне клиента `requests.Session`).
5. Посчитать throughput и построить графики.

## Инструменты

`requests`, mock-сервер, matplotlib.

## Какие файлы редактировать

- `tests/performance/test_download_sources.py`

## Рекомендуемые вспомогательные методы

| Метод | Файл | Назначение | Аргументы | Возвращает | Пример |
|---|---|---|---|---|---|
| `measure_download` | `network_helper.py` | Полное скачивание | url, timeout, expected_bytes | dict | `measure_download(url)` |
| `calculate_throughput` | `network_helper.py` | байт/с | bytes, duration_ms | float | `calculate_throughput(size, ms)` |
| `download_measurement` | `network_helper.py` | Measurement | url, scenario, source | Measurement | `download_measurement(url, 'local', 'local')` |
| `HttpClient` | `network_helper.py` | Сессия | base_url | клиент | `HttpClient(mock_server['url'])` |
| `plot_download_comparison` | `chart_helper.py` | Графики | rows | list[Path] | `plot_download_comparison(rows)` |
| `save_measurements` | `metrics_helper.py` | CSV | rows, name | Path | `save_measurements(rows, 'downloads.csv')` |

## Как запустить тест

```bash
pytest tests/performance/test_download_sources.py
```

## Как получить результаты

CSV и PNG в `reports/`.

## Как построить график

`plot_download_comparison` строит время, throughput, кеш и влияние задержки, если соответствующие `scenario`/`source` заполнены.

## Ожидаемый результат

Сравнение источников, непрохождение incomplete как success, выводы о влиянии delay и throttle.

## Критерии приёмки

Есть измерения local/cdn/delayed/throttle, проверки error/timeout/incomplete, cold vs warm, CSV и графики.

## Дополнительно

Сравнить `X-Cache` заголовок mock CDN с локальным ответом.
