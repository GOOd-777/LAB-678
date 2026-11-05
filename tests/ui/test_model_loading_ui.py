"""Лабораторная 1. UI-проверки загрузки моделей."""

from __future__ import annotations

import pytest


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_load_local_model(animation_page, lab_config):
    # TODO 1: Выбрать источник local и модель pulse-circle.
    # TODO 2: Нажать «Загрузить модель».
    # TODO 3: Дождаться статуса успешной загрузки.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_load_http_model(animation_page, lab_config):
    # TODO 1: Выбрать источник http.
    # TODO 2: Загрузить rotate-square.
    # TODO 3: Проверить имя загруженной модели.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_load_cdn_model(animation_page, lab_config):
    # TODO 1: Выбрать источник cdn.
    # TODO 2: Загрузить fade-circle.
    # TODO 3: Проверить, что модель отображается.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_load_model_error(animation_page, lab_config):
    # TODO 1: Выбрать источник errors.
    # TODO 2: Попытаться загрузить любую модель.
    # TODO 3: Проверить текст ошибки в #modelLoadError.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_loaded_model_is_visible(animation_page, lab_config):
    # TODO 1: Загрузить локальную модель.
    # TODO 2: Проверить класс фигуры или видимость 3D-куба.
    # TODO 3: Проверить #loadedModelName.
    pass


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.skip(reason="TODO: implement test")
def test_effect_runs_on_loaded_model(animation_page, lab_config):
    # TODO 1: Загрузить модель.
    # TODO 2: Запустить анимацию Pulse.
    # TODO 3: Проверить, что animationCount > 0 или playing is True.
    pass
