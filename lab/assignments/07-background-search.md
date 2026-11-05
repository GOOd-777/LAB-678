# Лабораторная работа 7. Поиск фоновых изображений и заставок

## Цель

Реализовать поиск фона и заставки, проверить краевые случаи и измерить производительность.

Студент пишет и функциональность (`findBackground`, `findScreensaver`), и тесты. Готового поиска в приложении нет.

## Краткая теория

Каталоги лежат в `test_assets/manifests/`. Есть совпадающие теги (`sunset`, `aurora`), повреждённые файлы (`broken`) и ссылки на несуществующие файлы (`missing`). `filterCatalogItems` только фильтрует по подстроке — стратегию коллизий и проверку доступности пишете вы.

## Что нужно сделать

1. Реализовать `findBackground` и `findScreensaver` в `student_api.js`.
2. Реализовать UI-тесты в `tests/ui/test_background_search_ui.py`.
3. Реализовать измерения в `tests/performance/test_background_search.py`.

## Как это сделать

1. Получить каталог `getBackgroundCatalog` / `getScreensaverCatalog`.
2. Отобрать кандидатов. Можно вызвать `filterCatalogItems`, но решение о коллизиях ваше.
3. Проверить ресурс `checkImageAvailability`.
4. Применить `applyStageBackground` / `applyScreensaver` или вернуть `null`.
5. Измерить время поиска при разных эффектах и числе пользователей.

Разделяйте время: обход каталога, HTTP-проверка, отображение.

## Инструменты

pytest, Selenium, `measureOperationTime`, matplotlib.

## Какие файлы редактировать

- `student_api.js`
- `tests/ui/test_background_search_ui.py`
- `tests/performance/test_background_search.py`

## Рекомендуемые вспомогательные методы

| Метод | Файл | Назначение | Аргументы | Возвращает | Пример |
|---|---|---|---|---|---|
| `getBackgroundCatalog` | `lab_utils.js` | Каталог фонов | — | `Promise<array>` | `await getBackgroundCatalog()` |
| `getScreensaverCatalog` | `lab_utils.js` | Каталог заставок | — | `Promise<array>` | `await getScreensaverCatalog()` |
| `filterCatalogItems` | `lab_utils.js` | Фильтр по подстроке | items, query, fields | array | `filterCatalogItems(items, 'sunset')` |
| `checkImageAvailability` | `lab_utils.js` | Доступность и валидность | url | `Promise<bool>` | `await checkImageAvailability(item.url)` |
| `applyStageBackground` | `lab_utils.js` | Показ фона | url | — | `applyStageBackground(item.url)` |
| `applyScreensaver` | `lab_utils.js` | Показ заставки | url | — | `applyScreensaver(item.url)` |
| `measureOperationTime` | `lab_utils.js` | Замер JS-операции | operation | `{result, durationMs}` | `await measureOperationTime(() => findBackground('sunset'))` |
| `plot_search_comparison` | `chart_helper.py` | График поиска | rows | list[Path] | `plot_search_comparison(rows)` |

`filterCatalogItems` не выбирает лучшее совпадение и не проверяет файлы.

## Локаторы

`#backgroundQuery`, `#findBackgroundBtn`, `#backgroundStatus`, `#screensaverQuery`, `#findScreensaverBtn`, `#screensaverStatus`.

## Как запустить тест

```bash
pytest tests/ui/test_background_search_ui.py tests/performance/test_background_search.py
```

## Как получить результаты

Статусы в UI, CSV и PNG в `reports/`.

## Как построить график

Постройте сравнение:

1. Время поиска по числу пользователей.
2. По типу эффекта.
3. При комбинации эффектов.
4. Успешный против неуспешного.
5. Фон против заставки.

Можно несколько вызовов `plot_comparison` / один `plot_search_comparison` с разными `scenario`.

## Ожидаемый результат

Рабочие методы поиска, функциональные проверки, CSV и графики.

## Критерии приёмки

- Методы больше не бросают `Not implemented`.
- Успех, неуспех, коллизии, broken и missing обработаны.
- Есть измерения и графики.
- Повреждённое изображение не применяется как фон.

## Дополнительно

Вернуть все валидные совпадения, а не только первое.
