# Лабораторная работа 4. Длительность одного цикла анимации

## Цель

Реализовать измерение одного цикла анимации и сравнить длительность Pulse, Rotate, Slide, Fade, Bounce и Rotate + Pulse на скоростях 0.5, 1.0, 2.0, 3.0.

Студент пишет и метод `measure_animation_cycle`, и тесты измерений.

## Краткая теория

Один цикл — одно повторение бесконечной анимации, а не ожидание её окончания. Базовые длительности: Pulse 1200, Rotate 3000, Slide 2000, Fade 1500, Bounce 1500 мс, делённые на скорость. У комбинации длительности разные — измеряйте каждый эффект отдельно. Запуск браузера в измерение не входит.

Используйте Web Animations API (`element.getAnimations()`, `currentTime`, `getComputedTiming`) и `performance.now()` внутри браузера.

## Что нужно сделать

1. Реализовать `measure_animation_cycle(driver, effect_index=0)` в `tests/helpers/metrics_helper.py`.
2. Реализовать измерения в `tests/performance/test_animation_cycle.py`.
3. Построить графики готовыми утилитами.
4. Удалить `skip` только у готовых тестов.

## Как это сделать

1. Реализовать `measure_animation_cycle` по требованиям в docstring метода.
2. Выбрать эффект и скорость готовыми хелперами, запустить анимацию.
3. Вызвать реализованный `measure_animation_cycle` (для нескольких повторений можно использовать `collect_cycle_measurements`).
4. Для комбинации измерить циклы по разным `effect_index`.
5. Сохранить CSV и вызвать `plot_animation_cycle_comparison`.

## Инструменты

Selenium `execute_async_script`, `performance.now()` в браузере, Web Animations API, matplotlib, CSV.

## Какие файлы редактировать

- `tests/helpers/metrics_helper.py` — метод `measure_animation_cycle`
- `tests/performance/test_animation_cycle.py`

## Рекомендуемые вспомогательные методы

| Метод | Файл | Назначение | Аргументы | Возвращает | Пример |
|---|---|---|---|---|---|
| `wait_for_running_animations` | `animation_helper.py` | Дождаться WAAPI | `driver`, `minimum` | list | `wait_for_running_animations(driver, 1)` |
| `get_running_animations_info` | `animation_helper.py` | Список анимаций | `driver` | list[dict] | `get_running_animations_info(driver)` |
| `collect_cycle_measurements` | `metrics_helper.py` | Несколько повторений через ваш метод | `driver`, `repeats`, `scenario`, `effect`, `speed` | list | `collect_cycle_measurements(driver, 3, 'pulse', 'pulse', 1.0)` |
| `calculate_statistics` | `metrics_helper.py` | mean/median/p95/stdev | iterable | dict | `calculate_statistics(values)` |
| `save_measurements` | `metrics_helper.py` | CSV в reports/ | rows, filename | Path | `save_measurements(rows, 'cycles.csv')` |
| `plot_animation_cycle_comparison` | `chart_helper.py` | Три графика | rows | list[Path] | `plot_animation_cycle_comparison(rows)` |
| `select_animation` / `set_animation_speed` / `start_animation` | `animation_helper.py` | Управление UI | см. модуль | — | `select_animation(driver, 'pulse')` |

Метод `measure_animation_cycle` студент реализует сам. Остальные утилиты уже готовы.

### Контракт `measure_animation_cycle`

- **Файл:** `tests/helpers/metrics_helper.py`
- **Аргументы:** `driver`, `effect_index=0`
- **Возвращает:** `dict` с полями `durationMs`, `configuredMs`, `effectIndex`
- **Условие:** анимация уже запущена; запуск браузера и выбор эффекта в измерение не входят

## Как запустить тест

```bash
pytest tests/performance/test_animation_cycle.py
```

Полная матрица 6×4 может занять несколько минут: Rotate на 0.5 — около 6 с на цикл.

## Как получить результаты

`reports/*cycle*.csv` и PNG.

## Как построить график

Утилита строит:

1. Длительность по типам эффектов.
2. Длительность от скорости.
3. Одиночные против комбинированных.

## Ожидаемый результат

Рабочий `measure_animation_cycle`, CSV с повторениями, статистика и три PNG. Более высокая скорость уменьшает цикл.

## Критерии приёмки

- `measure_animation_cycle` больше не бросает `NotImplementedError`.
- Есть измерения всех шести эффектов и четырёх скоростей хотя бы в сводном тесте.
- Браузер не входит в замер.
- Есть median, mean, p95 и разброс.

## Дополнительно

Сравнить измеренный цикл с `expected_cycle_ms(key, speed)`.
