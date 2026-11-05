"""Лабораторная 1. E2E-сценарии загрузки моделей."""

from __future__ import annotations

import pytest


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_load_model_from_source_end_to_end(animation_page, lab_config):
    # TODO 1: Войти в сессию (фикстура уже делает это).
    # TODO 2: Загрузить модель через выбранный источник.
    # TODO 3: Проверить статус и имя модели.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_loaded_model_appears_on_stage(animation_page):
    # TODO 1: Загрузить CSS-модель.
    # TODO 2: Проверить #shape или #model3d на сцене.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_start_animation_after_load(animation_page):
    # TODO 1: Загрузить модель.
    # TODO 2: Нажать Старт.
    # TODO 3: Дождаться активного состояния анимации.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_model_load_visible_in_session_feed(animation_page, app_server):
    # TODO 1: Загрузить модель.
    # TODO 2: При необходимости отправить действие через UI.
    # TODO 3: Проверить ленту или /api/room, если сценарий это поддерживает.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_recover_after_failed_load(animation_page, lab_config):
    # TODO 1: Вызвать ошибку загрузки.
    # TODO 2: Затем загрузить корректную локальную модель.
    # TODO 3: Проверить восстановление статуса.
    pass


@pytest.mark.student
@pytest.mark.e2e
@pytest.mark.skip(reason="TODO: implement test")
def test_load_model_in_user_session(animation_page, isolated_room):
    # TODO 1: Убедиться, что пользователь в сессии.
    # TODO 2: Загрузить модель.
    # TODO 3: Проверить, что сессия осталась активной.
    pass
