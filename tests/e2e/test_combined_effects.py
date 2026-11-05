"""Лабораторная 2. Совмещение анимаций и эффектов."""

from __future__ import annotations

import pytest


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_rotate_plus_pulse_can_start(animation_page):
    # TODO 1: Включить «Комбинировать: Вращение + Пульс».
    # TODO 2: Выбрать Pulse или Rotate и нажать Старт.
    # TODO 3: Проверить, что запущено больше одной анимации.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_combined_effects_are_both_active(animation_page):
    # TODO 1: Запустить комбинацию.
    # TODO 2: Прочитать window.motionGetAnimationsInfo().
    # TODO 3: Проверить playState и duration каждой анимации, не только CSS-класс.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_combined_effects_change_speed(animation_page):
    # TODO 1: Запустить комбинацию на скорости 1.0.
    # TODO 2: Изменить скорость на 2.0.
    # TODO 3: Сравнить duration до и после.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_combined_effects_stop_cleanly(animation_page):
    # TODO 1: Запустить комбинацию.
    # TODO 2: Нажать Стоп.
    # TODO 3: Проверить playing is False и отсутствие активных анимаций.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_combined_effects_can_restart(animation_page):
    # TODO 1: Запустить, остановить и запустить снова.
    # TODO 2: Проверить, что анимации снова активны.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_effects_are_independent_for_two_users(app_server, browser, lab_config):
    # TODO 1: Создать второго пользователя через API.
    # TODO 2: У одного включить combine, у другого нет.
    # TODO 3: Проверить /api/room: состояния не перезаписывают друг друга.
    pass
