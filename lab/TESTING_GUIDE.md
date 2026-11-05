# Краткое руководство по тестированию

## pytest

```bash
pytest -m "not student"          # только инфраструктура
pytest tests/e2e/test_combined_effects.py -k rotate
pytest -n auto                   # pytest-xdist, каждый воркер получает свой порт
```

Студенческие тесты помечаются `@pytest.mark.student` и до реализации должны быть `@pytest.mark.skip`.

## Selenium

Фикстура `animation_page` уже:

1. Запускает `room_server.py` на свободном порту.
2. Открывает Chrome в headless-режиме.
3. Входит в сессию.
4. Показывает локальную модель на сцене (`body.lab-show-local-actor`).
5. Подставляет URL mock-источников.

Основные локаторы:

| Элемент | Локатор |
|---|---|
| Имя | `#entryUserName` |
| Войти | `#entryConnectBtn` |
| Анимация | `#anim-pulse`, `#anim-rotate`, `#anim-slide`, `#anim-fade`, `#anim-bounce` |
| Старт / Стоп | `#startBtn`, `#stopBtn` |
| Скорость | `#speed` |
| 3D | `#use3d` |
| Комбинация | `#combine` |
| Источник модели | `#modelSourceSelect` |
| Идентификатор | `#modelIdInput` |
| Загрузить | `#loadModelBtn` |

Не используйте фиксированный `time.sleep()`, если можно дождаться состояния:

```python
from tests.helpers.animation_helper import wait_for_animation_state
wait_for_animation_state(driver, playing=True)
```

## HTTP

```python
from tests.helpers.session_helper import create_test_session, post_action
session = create_test_session(app_server["url"], "anna")
post_action(app_server["url"], session["userId"], "start", "запустил анимацию")
```

## E2E

Один сценарий — один тестовый метод. Большой поток лучше разбить:

1. Войти.
2. Выбрать эффект.
3. Проверить состояние.
4. Остановить.

## Ожидание без sleep

```python
from tests.helpers.browser_helper import wait_for_condition
wait_for_condition(driver, lambda d: d.find_element("id", "sessionBadge").text != "Не подключено")
```

## Метрики

```python
from tests.helpers.metrics_helper import measure_duration, calculate_statistics, save_measurements
result, ms = measure_duration(lambda: client.get("/api/room"))
stats = calculate_statistics([ms])
```

Для анимаций (метод `measure_animation_cycle` реализует студент в лабораторной 4):

```python
from tests.helpers.metrics_helper import measure_animation_cycle
# анимация уже запущена
sample = measure_animation_cycle(driver)
# sample["durationMs"], sample["configuredMs"]
```

## Графики

```python
from tests.helpers.chart_helper import plot_comparison, plot_animation_cycle_comparison
plot_comparison(["pulse", "rotate"], [1200, 3000], "Цикл", "Эффект", "мс", "cycles.png")
```

## Page Object

```python
animation_page.select_effect("rotate")
animation_page.set_combine(True)
animation_page.start()
```
