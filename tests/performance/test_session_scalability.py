"""Лабораторная 5. Производительность при росте числа сессий."""

from __future__ import annotations

import pytest

USER_COUNTS = (1, 5, 10, 25, 50)


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_join_latency_scales_with_users(isolated_room):
    # TODO 1: Создать 1, 5, 10, 25, 50 пользователей через HTTP.
    # TODO 2: Измерить время /api/join. Не использовать Selenium для нагрузки.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_action_and_room_latency(isolated_room):
    # TODO 1: Для каждого размера группы измерить /api/action и /api/room.
    # TODO 2: Сохранить Measurement.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_sse_delivery_delay(isolated_room):
    # TODO 1: Подключить один SSE-клиент.
    # TODO 2: Отправить action и измерить задержку до получения события.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_throughput_and_errors(isolated_room):
    # TODO 1: Зафиксировать число успешных запросов в секунду.
    # TODO 2: Посчитать процент ошибок.
    pass


@pytest.mark.student
@pytest.mark.performance
@pytest.mark.skip(reason="TODO: implement test")
def test_save_scalability_charts(isolated_room, reports_dir):
    # TODO 1: Собрать latency, throughput, error rate и SSE delay.
    # TODO 2: Сохранить CSV и построить 4 графика.
    pass


@pytest.mark.load
@pytest.mark.student
@pytest.mark.skip(reason="TODO: optional 100 users")
def test_optional_one_hundred_users(isolated_room):
    # TODO: Дополнительно проверить 100 пользователей.
    pass
