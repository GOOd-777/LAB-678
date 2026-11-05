"""Лабораторная 3. Отрисовка 2D и 3D."""

from __future__ import annotations

import pytest


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_2d_model_is_visible(animation_page):
    # TODO 1: Выключить 3D.
    # TODO 2: Проверить, что #shape видим, а #model3d скрыт.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_switch_to_3d(animation_page):
    # TODO 1: Включить чекбокс #use3d.
    # TODO 2: Проверить, что #model3d больше не имеет класс hidden.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_3d_has_transform(animation_page):
    # TODO 1: Включить 3D.
    # TODO 2: Прочитать computed transform у #model3d.
    # TODO 3: Убедиться, что есть rotateX/rotateY или matrix3d.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_return_to_2d(animation_page):
    # TODO 1: Включить 3D, затем выключить.
    # TODO 2: Проверить возврат 2D-фигуры.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_no_unexpected_overlap(animation_page, reports_dir):
    # TODO 1: Сделать скриншоты 2D и 3D.
    # TODO 2: Сравнить bounds #shape и #model3d.
    # TODO 3: Они не должны быть видимы одновременно.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_render_at_different_window_sizes(animation_page):
    # TODO 1: Проверить сцену на 1280x800 и 800x600.
    # TODO 2: Элемент #stage должен оставаться в пределах окна.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_model_visible_during_animation(animation_page):
    # TODO 1: Запустить Pulse.
    # TODO 2: Снять скриншот сцены.
    # TODO 3: Проверить, что актор имеет ненулевой размер.
    pass
