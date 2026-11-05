"""Page Object для основных элементов Motion Playground."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from tests.helpers.animation_helper import (
    select_animation,
    set_3d,
    set_animation_speed,
    set_combine,
    start_animation,
    stop_animation,
)
from tests.helpers.browser_helper import show_local_actor
from tests.helpers.session_helper import login_via_ui


class MotionPage:
    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url

    def open_and_login(self, name: str | None = None) -> str:
        user_name = login_via_ui(self.driver, self.base_url, name)
        show_local_actor(self.driver)
        return user_name

    def select_effect(self, key: str) -> None:
        select_animation(self.driver, key)

    def start(self) -> None:
        start_animation(self.driver)

    def stop(self) -> None:
        stop_animation(self.driver)

    def set_speed(self, speed: float) -> None:
        set_animation_speed(self.driver, speed)

    def set_combine(self, enabled: bool) -> None:
        set_combine(self.driver, enabled)

    def set_3d(self, enabled: bool) -> None:
        set_3d(self.driver, enabled)

    def load_model(self, source_type: str, model_id: str) -> None:
        Select(self.driver.find_element(By.ID, "modelSourceSelect")).select_by_value(source_type)
        field = self.driver.find_element(By.ID, "modelIdInput")
        field.clear()
        field.send_keys(model_id)
        self.driver.find_element(By.ID, "loadModelBtn").click()

    def search_background(self, query: str) -> None:
        field = self.driver.find_element(By.ID, "backgroundQuery")
        field.clear()
        field.send_keys(query)
        self.driver.find_element(By.ID, "findBackgroundBtn").click()

    def search_screensaver(self, query: str) -> None:
        field = self.driver.find_element(By.ID, "screensaverQuery")
        field.clear()
        field.send_keys(query)
        self.driver.find_element(By.ID, "findScreensaverBtn").click()

    @property
    def session_badge(self) -> str:
        return self.driver.find_element(By.ID, "sessionBadge").text

    @property
    def model_status(self) -> str:
        return self.driver.find_element(By.ID, "modelLoadStatus").text
