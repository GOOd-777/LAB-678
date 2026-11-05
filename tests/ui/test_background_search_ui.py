from __future__ import annotations

import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


def _driver(animation_page):
    return animation_page.driver


def _search(driver, query: str, button_id: str, input_id: str, status_id: str):
    field = driver.find_element(By.ID, input_id)
    field.clear()
    field.send_keys(query)

    driver.find_element(By.ID, button_id).click()

    WebDriverWait(driver, 15).until(
        lambda d: d.find_element(By.ID, status_id).text
        and "…" not in d.find_element(By.ID, status_id).text
    )

    return driver.find_element(By.ID, status_id).text


@pytest.mark.student
@pytest.mark.ui
def test_successful_background_search(animation_page):
    driver = _driver(animation_page)

    status = _search(
        driver,
        "sunset",
        "findBackgroundBtn",
        "backgroundQuery",
        "backgroundStatus",
    )

    assert "Найдено фонов:" in status
    assert "Применён:" in status

    backdrop = driver.find_element(By.ID, "stageBackdrop")

    assert backdrop.is_displayed() or backdrop.get_attribute("hidden") is None


@pytest.mark.student
@pytest.mark.ui
def test_unsuccessful_background_search(animation_page):
    driver = _driver(animation_page)

    status = _search(
        driver,
        "definitely_nonexistent_background_987654",
        "findBackgroundBtn",
        "backgroundQuery",
        "backgroundStatus",
    )

    assert status == "Фон не найден"


@pytest.mark.student
@pytest.mark.ui
def test_background_collisions(animation_page):
    driver = _driver(animation_page)

    status = _search(
        driver,
        "sunset",
        "findBackgroundBtn",
        "backgroundQuery",
        "backgroundStatus",
    )

    assert "Найдено фонов:" in status

    # Проверяем, что поиск вернул несколько результатов,
    # а не только первое совпадение.
    count = int(status.split("Найдено фонов:")[1].split(".")[0])

    assert count >= 2


@pytest.mark.student
@pytest.mark.ui
@pytest.mark.parametrize("query", ["broken", "missing"])
def test_broken_and_missing_images(animation_page, query):
    driver = _driver(animation_page)

    # Считаем события применения до поиска.
    events_before = driver.execute_script("""
        return window.motionBrowserEvents.filter(
            event => event.name === "background-applied"
        ).length;
    """)

    status = _search(
        driver,
        query,
        "findBackgroundBtn",
        "backgroundQuery",
        "backgroundStatus",
    )

    events_after = driver.execute_script("""
        return window.motionBrowserEvents.filter(
            event => event.name === "background-applied"
        ).length;
    """)

    assert status == "Фон не найден"

    # Невалидное изображение не должно применяться.
    assert events_after == events_before