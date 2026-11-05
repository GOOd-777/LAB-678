
"""Лабораторная 6. Наблюдаемость событий."""

from __future__ import annotations

import csv
import json
import re
import time

import pytest
import requests
from selenium.webdriver.common.by import By

from tests.helpers.event_helper import (
    EVENT_CATALOG,
    SseClient,
    collect_browser_events,
    collect_server_feed,
    collect_ui_feed,
)
from tests.helpers.event_helper import (
    EVENT_CATALOG,
    SseClient,
    collect_browser_events,
    collect_server_feed,
    collect_ui_feed,
)
from tests.helpers.session_helper import get_server_logs


def _driver(page):
    """Получить Selenium WebDriver из MotionPage."""
    driver = getattr(page, "driver", None)
    if driver is None:
        raise RuntimeError(
            "Не найден WebDriver в animation_page. "
            "Проверь атрибут MotionPage.driver."
        )
    return driver


def _contains_event(event, *names):
    """Проверить тип события, включая вложенные данные SSE."""
    if not isinstance(event, dict):
        return False

    values = [event.get("type"), event.get("action")]

    for key in ("data", "payload", "state"):
        nested = event.get(key)
        if isinstance(nested, dict):
            values.extend([nested.get("type"), nested.get("action")])

    return any(
        isinstance(value, str)
        and any(name in value.lower() for name in names)
        for value in values
    )


def _wait_feed(url, predicate, timeout=5):
    deadline = time.time() + timeout

    while time.time() < deadline:
        feed = collect_server_feed(url)
        for event in feed:
            if predicate(event):
                return event
        time.sleep(0.1)

    return None


def _click_button(driver, patterns):
    """Найти кнопку по тексту или aria-label."""
    for element in driver.find_elements(By.CSS_SELECTOR, "button"):
        text = (
            element.text + " " +
            (element.get_attribute("aria-label") or "") + " " +
            (element.get_attribute("title") or "")
        ).lower()

        if any(re.search(pattern, text) for pattern in patterns):
            if element.is_displayed() and element.is_enabled():
                element.click()
                return True

    return False


def _event_types(events):
    return {
        str(event.get("type", "")).lower()
        for event in events
        if isinstance(event, dict)
    }


@pytest.mark.student
@pytest.mark.observability
def test_registered_join_event(animation_page, app_server):
    """Проверка зарегистрированного события подключения."""
    url = app_server["url"]
    user_name = animation_page.user_name

    feed = collect_server_feed(url)

    joins = [
        event for event in feed
        if event.get("type") == "join"
    ]

    assert joins, f"Событие join отсутствует в feed: {feed}"

    assert any(
        user_name in json.dumps(event, ensure_ascii=False)
        for event in joins
    ), f"Не найден join пользователя {user_name}"


@pytest.mark.student
@pytest.mark.observability
def test_event_sequence_start_stop(animation_page, app_server):
    """Проверка последовательности start -> stop."""
    driver = _driver(animation_page)
    url = app_server["url"]

    initial_feed = collect_server_feed(url)
    initial_count = len(initial_feed)

    started = _click_button(
        driver,
        [r"start", r"запуск", r"старт", r"play"],
    )

    assert started, "Не найдена кнопка запуска анимации"

    start_event = _wait_feed(
        url,
        lambda event: _contains_event(
            event, "start", "animation"
        ),
    )
    assert start_event is not None, "Событие запуска не найдено"

    stopped = _click_button(
        driver,
        [r"stop", r"останов", r"стоп", r"pause"],
    )

    assert stopped, "Не найдена кнопка остановки"

    stop_event = _wait_feed(
        url,
        lambda event: event.get("type") == "stop",
    )
    assert stop_event is not None, "Событие stop не найдено"

    feed = collect_server_feed(url)
    new_events = feed[initial_count:]

    start_index = next(
        (
            i for i, event in enumerate(new_events)
            if _contains_event(event, "start", "animation")
        ),
        None,
    )

    stop_index = next(
        (
            i for i, event in enumerate(new_events)
            if event.get("type") == "stop"
        ),
        None,
    )

    assert start_index is not None
    assert stop_index is not None
    assert start_index < stop_index, (
        f"Неверный порядок событий: {new_events}"
    )


@pytest.mark.student
@pytest.mark.observability
def test_sse_events_match_actions(animation_page, app_server):
    """Проверка передачи изменения скорости по SSE."""
    driver = _driver(animation_page)
    url = app_server["url"]

    client = SseClient(url).start()

    try:
        speed = driver.find_element(By.ID, "speed")

        old_value = speed.get_attribute("value")
        new_value = "1.5" if old_value != "1.5" else "1.2"

        driver.execute_script(
            """
            const element = document.querySelector('#speed');
            element.value = arguments[0];
            element.dispatchEvent(
                new Event('input', {bubbles: true})
            );
            element.dispatchEvent(
                new Event('change', {bubbles: true})
            );
            """,
            new_value,
        )

        event = client.wait_for(
            lambda item: (
                item.get("type") == "speed"
                or _contains_event(item, "speed")
            ),
            timeout=8,
        )

        # Некоторые реализации передают действия как type=action.
        if event is None:
            event = client.wait_for(
                lambda item: (
                    item.get("type") == "action"
                    and "speed" in json.dumps(item).lower()
                ),
                timeout=3,
            )

        assert event is not None, (
            f"SSE-событие изменения скорости не получено. "
            f"Полученные события: {client.events}"
        )

        assert any(
            _contains_event(item, "speed")
            or (
                item.get("type") == "action"
                and "speed" in json.dumps(item).lower()
            )
            for item in client.events
        )

    finally:
        client.stop()


@pytest.mark.student
@pytest.mark.observability
def test_missing_model_error_is_not_in_server_feed(
    animation_page, app_server
):
    """Ошибка загрузки модели не входит в серверный контракт."""
    driver = _driver(animation_page)
    url = app_server["url"]

    before = collect_server_feed(url)

    # Имитируем клиентское событие ошибки загрузки модели.
    driver.execute_script(
        """
        window.dispatchEvent(new CustomEvent(
            'motion:model-load-error',
            {detail: {message: 'Test model load error'}}
        ));
        """
    )

    time.sleep(0.3)

    browser_events = collect_browser_events(driver)
    ui_feed = collect_ui_feed(driver)
    server_feed = collect_server_feed(url)

    # Ошибка может отображаться на клиенте, но не обязана
    # регистрироваться сервером.
    assert not any(
        _contains_event(event, "model-load-error")
        for event in server_feed
    )

    assert not any(
        _contains_event(event, "model-load-error")
        for event in get_server_logs(url).get("events", [])
    )

    # Проверяем, что проверка отсутствующего события
    # не требует его появления в серверном feed.
    assert isinstance(browser_events, list)
    assert isinstance(ui_feed, list)
    assert isinstance(before, list)


@pytest.mark.student
@pytest.mark.observability
def test_failed_http_request_observability(app_server):
    """Неуспешный HTTP-запрос не создаёт событие feed."""
    url = app_server["url"]

    before = collect_server_feed(url)

    response = requests.post(
        f"{url}/api/join",
        json={"name": ""},
        timeout=5,
    )

    assert response.status_code >= 400, (
        f"Ожидалась ошибка HTTP, получено {response.status_code}"
    )

    after = collect_server_feed(url)

    # Ошибочный запрос не должен создавать join.
    assert after == before, (
        "Неуспешный HTTP-запрос изменил серверный feed"
    )

    assert not any(
        event.get("type") == "join"
        and not event.get("name")
        for event in after
    )


@pytest.mark.student
@pytest.mark.observability
def test_build_event_coverage_table(
    animation_page, app_server, reports_dir
):
    """Формирование CSV-таблицы наблюдаемости."""
    driver = _driver(animation_page)
    url = app_server["url"]

    feed = collect_server_feed(url)
    logs = get_server_logs(url)
    browser_events = collect_browser_events(driver)
    ui_events = collect_ui_feed(driver)

    # События, найденные в серверном feed.
    feed_types = _event_types(feed)

    # Дополнительные серверные логи.
    logs_text = json.dumps(logs, ensure_ascii=False).lower()

    # События браузера и текст UI.
    browser_text = json.dumps(
        browser_events, ensure_ascii=False
    ).lower()

    ui_text = " ".join(ui_events).lower()

    # События SSE проверяются отдельным подключением.
    client = SseClient(url).start()

    try:
        time.sleep(0.5)
        sse_events = list(client.events)
    finally:
        client.stop()

    sse_types = _event_types(sse_events)
    sse_text = json.dumps(
        sse_events, ensure_ascii=False
    ).lower()

    event_mapping = {
        "Подключение": ["join"],
        "Отключение": ["leave"],
        "Запуск анимации": ["start", "animation"],
        "Остановка": ["stop"],
        "Изменение скорости": ["speed"],
        "Изменение эффекта": ["animation", "effect"],
        "Переключение 2D/3D": ["mode"],
        "Ошибка загрузки модели": ["motion:model-load-error"],
        "Потеря SSE": ["connection lost", "соединение потеряно"],
        "Повторное подключение": ["join"],
        "Неуспешный HTTP-запрос": ["http_error", "request_error"],
    }

    output = reports_dir / "event-coverage.csv"

    with output.open(
        "w", newline="", encoding="utf-8-sig"
    ) as csv_file:
        writer = csv.writer(csv_file, delimiter=";")

        writer.writerow([
            "Событие",
            "UI",
            "SSE",
            "Серверные логи",
            "Обнаружено",
            "Контракт",
            "Примечание",
        ])

        for item in EVENT_CATALOG:
            name = item["event"]
            keywords = event_mapping.get(name, [])

            ui_found = (
                any(word in ui_text for word in keywords)
                or any(
                    word in browser_text for word in keywords
                )
            )

            sse_found = (
                any(word in sse_types for word in keywords)
                or any(word in sse_text for word in keywords)
            )

            server_found = (
                any(word in feed_types for word in keywords)
                or any(word in logs_text for word in keywords)
            )

            detected = ui_found or sse_found or server_found

            writer.writerow([
                name,
                "да" if ui_found else "нет",
                "да" if sse_found else "нет",
                "да" if server_found else "нет",
                "да" if detected else "нет",
                "да" if item.get("contract") else "нет",
                item.get("note", ""),
            ])

    assert output.exists()
    assert output.stat().st_size > 0
