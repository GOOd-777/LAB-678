# Лабораторные работы Motion Playground Web

Набор из восьми небольших заданий по UI/E2E-тестам, измерениям производительности и наблюдаемости событий.

Студент реализует функциональность и тесты, которые являются предметом задания. Инфраструктура (Selenium, mock-серверы, фикстуры, графики, HTTP-клиент) уже готова.

## Порядок выполнения

1. Загрузка моделей из разных источников.
2. Совмещение анимаций и эффектов.
3. Отрисовка 2D и 3D.
4. Длительность одного цикла анимации.
5. Производительность при росте числа сессий.
6. Наблюдаемость событий.
7. Поиск фона и заставки.
8. Скорость скачивания из разных источников.

Задания 1 и 7 требуют и кода приложения, и тестов. Задание 4 — реализацию `measure_animation_cycle` и тестов измерений. Остальные задания опираются на уже существующие возможности приложения.

## Требования к окружению

- Python 3.10+ (предпочтительно 3.11+).
- Google Chrome / Chromium.
- Современный браузер для ручного запуска приложения.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-test.txt
```

Если `python3 -m venv` сообщает об отсутствии `ensurepip`:

```bash
python3 -m venv --without-pip .venv
curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
.venv/bin/python /tmp/get-pip.py
.venv/bin/pip install -r requirements-test.txt
```

Тестовые ресурсы уже лежат в `test_assets/`. При необходимости пересоздайте их:

```bash
python3 test_infrastructure/scripts/generate_assets.py
```

## Запуск приложения

```bash
python3 room_server.py
```

Откройте http://127.0.0.1:8080, введите имя и войдите в сессию.

## Запуск тестов

Инфраструктура без студенческих заданий:

```bash
pytest -m "not student"
```

По каталогам:

```bash
pytest tests/ui/
pytest tests/e2e/
pytest tests/performance/
pytest tests/observability/
pytest tests/smoke/
```

Пока методы с `TODO` не реализованы, студенческие тесты имеют статус `SKIPPED`.

Тяжёлая нагрузка запускается отдельно:

```bash
./test_infrastructure/scripts/run_load_test.sh
```

## Графики и результаты

Готовые утилиты сохраняют CSV и PNG в `reports/`.

```python
from tests.helpers.metrics_helper import save_measurements
from tests.helpers.chart_helper import plot_animation_cycle_comparison
```

Демонстрационный график (не лабораторное измерение):

```bash
python3 -c "from tests.helpers.chart_helper import plot_demo_chart; plot_demo_chart()"
```

## Сдача

1. Реализовать требуемые методы и тесты.
2. Удалить `@pytest.mark.skip` только у реализованных тестов.
3. Приложить CSV/PNG из `reports/`, если задание этого требует.
4. Не копировать файлы из `instructor_solutions/`.
