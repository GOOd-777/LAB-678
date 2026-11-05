# Лабораторная работа 1. Загрузка моделей из разных источников

## Цель

Реализовать загрузку CSS-моделей из локального каталога, HTTP и mock CDN и подтвердить это UI- и E2E-тестами.

Студент пишет и функциональность (`loadModel`), и тесты. Готовой загрузки в приложении нет.

## Краткая теория

Приложение показывает CSS-фигуры и CSS-куб. Отдельного 3D-движка нет. «Модель» — JSON с полями `id`, `name`, `type`, `shape`, `previewColor`, `stageBackground`, `use3d`.

## Что нужно сделать

1. Реализовать `loadModel(sourceType, modelId)` в `student_api.js`.
2. Реализовать UI-тесты в `tests/ui/test_model_loading_ui.py`.
3. Реализовать E2E-тесты в `tests/e2e/test_model_loading_e2e.py`.
4. Удалить `skip` только у готовых тестов.

## Как это сделать

1. По `sourceType` взять базовый URL через `getConfiguredSourceBaseUrl`.
2. Собрать адрес `{base}/{modelId}.json`.
3. Вызвать `fetchModelResource`.
4. Проверить данные `validateModelData` и привести их `normalizeModelData`.
5. Отрисовать `renderLoadedModel` либо показать ошибку `showModelLoadError`.
6. В тестах использовать `animation_page.load_model(...)` и проверки статуса.

## Инструменты

pytest, Selenium, `requests` (для API-части E2E), mock-сервер из фикстуры `mock_server`.

## Какие файлы редактировать

- `student_api.js` — метод `loadModel`.
- `tests/ui/test_model_loading_ui.py`
- `tests/e2e/test_model_loading_e2e.py`

Не нужно настраивать Chrome и порты.

## Рекомендуемые вспомогательные методы

| Метод | Файл | Назначение | Аргументы | Возвращает | Пример |
|---|---|---|---|---|---|
| `getConfiguredSourceBaseUrl` | `lab_utils.js` | Базовый URL источника | `sourceType` | `string` | `getConfiguredSourceBaseUrl('local')` |
| `fetchModelResource` | `lab_utils.js` | HTTP GET | `url` | JSON/text | `await fetchModelResource(url)` |
| `validateModelData` | `lab_utils.js` | Проверка структуры | `data` | `bool` | `validateModelData(data)` |
| `normalizeModelData` | `lab_utils.js` | Приведение к формату сцены | `data` | объект модели | `normalizeModelData(data)` |
| `renderLoadedModel` | `lab_utils.js` | Показ уже готовой модели | `model` | `model` | `renderLoadedModel(model)` |
| `showModelLoadError` | `lab_utils.js` | Показ ошибки | `message` | — | `showModelLoadError(err.message)` |
| `MotionPage.load_model` | `tests/helpers/page_objects.py` | UI-действие | `source`, `id` | — | `animation_page.load_model('http', 'rotate-square')` |

## Локаторы

`#modelSourceSelect`, `#modelIdInput`, `#loadModelBtn`, `#modelLoadStatus`, `#modelLoadError`, `#loadedModelName`, `#shape`, `#model3d`.

Доступные модели: `pulse-circle`, `rotate-square`, `slide-square`, `fade-circle`, `bounce-square`, `cube-3d`.

## Как запустить тест

```bash
pytest tests/ui/test_model_loading_ui.py tests/e2e/test_model_loading_e2e.py
```

## Как получить результаты

pytest покажет `PASSED` у реализованных тестов. Статус и имя модели видны в UI.

## График

Не требуется.

## Ожидаемый результат

Модель загружается из `local`, `http` и `cdn`, ошибка источника отображается, после ошибки можно загрузить корректную модель, анимация запускается на загруженной модели, сессия остаётся активной.

## Критерии приёмки

- `loadModel` больше не бросает `Not implemented`.
- Три источника работают без внешних CDN.
- Ошибка не роняет страницу.
- UI и E2E тесты не пропущены и проходят.

## Дополнительно

Измерить время загрузки из `delayed` через `measureOperationTime`.
