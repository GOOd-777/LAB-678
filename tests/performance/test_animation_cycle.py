"""Лабораторная 4. Длительность одного цикла анимации."""

from __future__ import annotations

import pytest

EFFECTS = ("pulse", "rotate", "slide", "fade", "bounce")
SPEEDS = (0.5, 1.0, 2.0, 3.0)


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_measure_pulse_cycle(animation_page):
    # TODO 1: Реализовать measure_animation_cycle в metrics_helper.py (см. TODO в методе).
    # TODO 2: Выбрать Pulse и скорость 1.0.
    # TODO 3: Запустить анимацию.
    # TODO 4: Измерить один цикл через measure_animation_cycle.
    # TODO 5: Проверить, что durationMs > 200.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_measure_rotate_cycle(animation_page):
    # TODO 1: Выбрать Rotate.
    # TODO 2: Измерить один цикл, не включая запуск браузера.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_measure_slide_fade_bounce(animation_page):
    # TODO 1: Для Slide, Fade и Bounce измерить по одному циклу.
    # TODO 2: Сохранить результаты в список Measurement.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_measure_cycles_at_supported_speeds(animation_page):
    # TODO 1: Для Pulse измерить циклы на скоростях 0.5, 1.0, 2.0, 3.0.
    # TODO 2: Выполнить несколько повторений.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_measure_combined_rotate_pulse(animation_page):
    # TODO 1: Включить комбинацию.
    # TODO 2: Измерить циклы каждого эффекта отдельно (разные duration).
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_save_cycle_csv_and_charts(animation_page, reports_dir):
    # TODO 1: Собрать измерения по эффектам и скоростям.
    # TODO 2: Посчитать median, mean, p95 и разброс.
    # TODO 3: Сохранить CSV и построить графики готовыми утилитами.
    pass
