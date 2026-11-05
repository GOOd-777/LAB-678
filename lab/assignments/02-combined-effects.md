# Лабораторная работа 2. Совмещение анимаций и эффектов

## Цель

Проверить одновременную работу вращения и пульсации, смену скорости, остановку и независимость пользователей.

Новые комбинации добавлять не нужно. Приложение поддерживает только «Вращение + Пульс» (`#combine`).

## Краткая теория

Анимации запускаются через Web Animations API на `#actor`. При включённой комбинации создаются две анимации с разной длительностью: Pulse ≈ 1200 мс, Rotate ≈ 3000 мс (делятся на скорость). Проверки только по CSS-классу недостаточно.

## Что нужно сделать

Реализовать тесты в `tests/e2e/test_combined_effects.py`.

## Как это сделать

1. Войти через фикстуру `animation_page`.
2. Включить `#combine`.
3. Запустить эффект.
4. Прочитать `window.motionGetAnimationsInfo()`.
5. Изменить скорость и сравнить `duration`.
6. Остановить и проверить отсутствие активных анимаций.
7. Для двух пользователей сравнить `state` в `/api/room`.

## Инструменты

Selenium, WebDriverWait, Web Animations API, HTTP API.

## Какие файлы редактировать

- `tests/e2e/test_combined_effects.py`

## Рекомендуемые вспомогательные методы

| Метод | Файл | Назначение | Аргументы | Возвращает | Пример |
|---|---|---|---|---|---|
| `select_animation` | `animation_helper.py` | Выбор эффекта | `driver`, `key` | — | `select_animation(driver, 'pulse')` |
| `set_combine` | `animation_helper.py` | Комбинация | `driver`, `bool` | — | `set_combine(driver, True)` |
| `start_animation` / `stop_animation` | `animation_helper.py` | Старт/стоп | `driver` | — | `start_animation(driver)` |
| `set_animation_speed` | `animation_helper.py` | Скорость 0.5–3.0 | `driver`, `speed` | — | `set_animation_speed(driver, 2.0)` |
| `get_running_animations_info` | `animation_helper.py` | Состояние WAAPI | `driver` | `list[dict]` | `get_running_animations_info(driver)` |
| `wait_for_animation_state` | `animation_helper.py` | Ожидание playing | `driver`, `bool` | — | `wait_for_animation_state(driver, False)` |
| `create_test_session` | `session_helper.py` | Второй пользователь | `base_url`, `name` | dict | `create_test_session(url, 'bob')` |

## Как запустить тест

```bash
pytest tests/e2e/test_combined_effects.py
```

## Как получить результаты

Успешные проверки `playState`, числа анимаций и независимости `state` в `/api/room`.

## График

Не требуется.

## Ожидаемый результат

Комбинация запускает два эффекта, скорость меняет duration, стоп снимает активность, повторный старт работает, состояния пользователей независимы.

## Критерии приёмки

Все шесть тестов без `skip` проходят. Есть проверка через Web Animations API или computed style, не только класс.

## Дополнительно

Сравнить computed `transform` у `#actor` во время Pulse и Rotate + Pulse.
