# Лабораторная работа 3. Проверка отрисовки 2D и 3D

## Цель

Проверить, что 2D-фигура и CSS-куб корректно переключаются, имеют трансформации и не накладываются одновременно.

## Краткая теория

2D — `#shape` (круг/квадрат). 3D — `#model3d` с `transform-style: preserve-3d` и `rotateX/rotateY`. Чекбокс `#use3d` переключает видимость. Для скриншотов фикстура включает `lab-show-local-actor`.

## Что нужно сделать

Реализовать тесты в `tests/ui/test_rendering_2d_3d.py`.

## Как это сделать

1. Выключить 3D и проверить видимость `#shape`.
2. Включить 3D и проверить `#model3d`.
3. Прочитать computed transform.
4. Вернуться в 2D.
5. Сравнить bounds: одновременно виден только один вариант.
6. Повторить на окнах 1280×800 и 800×600.
7. Запустить анимацию и убедиться, что модель имеет ненулевой размер.

При сравнении скриншотов используйте погрешность `tolerance=0.08`.

## Инструменты

Selenium, скриншоты элемента, `compare_screenshots`.

## Какие файлы редактировать

- `tests/ui/test_rendering_2d_3d.py`

## Рекомендуемые вспомогательные методы

| Метод | Файл | Назначение | Аргументы | Возвращает | Пример |
|---|---|---|---|---|---|
| `set_3d` | `animation_helper.py` | Переключить режим | `driver`, `bool` | — | `set_3d(driver, True)` |
| `get_computed_transform` | `animation_helper.py` | Computed CSS | `driver`, `selector` | dict | `get_computed_transform(driver, '#model3d')` |
| `get_element_bounds` | `animation_helper.py` | Геометрия | `driver`, `selector` | dict | `get_element_bounds(driver, '#shape')` |
| `capture_model_screenshot` | `animation_helper.py` | Скриншот | `driver`, `path`, `selector` | path | `capture_model_screenshot(driver, str(reports_dir / '2d.png'))` |
| `compare_screenshots` | `animation_helper.py` | Сравнение | `a`, `b`, `tolerance` | dict | `compare_screenshots(a, b, 0.08)` |
| `set_window_size` | `browser_helper.py` | Размер окна | `driver`, `w`, `h` | — | `set_window_size(driver, 800, 600)` |

## Как запустить тест

```bash
pytest tests/ui/test_rendering_2d_3d.py
```

## Как получить результаты

Скриншоты сохраняйте в `reports/`.

## График

Не требуется. Скриншотное сравнение — с допустимой погрешностью.

## Ожидаемый результат

2D и 3D переключаются, у куба есть 3D-трансформация, одновременного показа фигуры и куба нет, сцена остаётся в окне.

## Критерии приёмки

Семь тестов проходят. Есть проверка transform и проверка на двух размерах окна.

## Дополнительно

Сравнить скриншот 2D и 3D: `similar` должно быть False при разумном tolerance.
