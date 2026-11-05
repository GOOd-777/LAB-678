"""Работа с тестовыми CSS-моделями и элементами сцены."""

from __future__ import annotations

from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select

from tests.helpers.browser_helper import js, wait_for_condition

ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = ROOT / "test_assets" / "models"


def list_test_models() -> list[str]:
    return sorted(path.stem for path in MODELS_DIR.glob("*.json"))


def get_model_path(model_id: str) -> Path:
    return MODELS_DIR / f"{model_id}.json"


def inject_lab_config(driver: WebDriver, config: dict) -> None:
    js(driver, "window.MOTION_LAB_CONFIG = arguments[0];", config)


def trigger_load_model_ui(driver: WebDriver, source_type: str, model_id: str) -> None:
    Select(driver.find_element(By.ID, "modelSourceSelect")).select_by_value(source_type)
    field = driver.find_element(By.ID, "modelIdInput")
    field.clear()
    field.send_keys(model_id)
    driver.find_element(By.ID, "loadModelBtn").click()


def get_loaded_model_status(driver: WebDriver) -> str:
    return driver.find_element(By.ID, "modelLoadStatus").text


def get_model_load_error(driver: WebDriver) -> str:
    return driver.find_element(By.ID, "modelLoadError").text


def wait_for_model_name(driver: WebDriver, expected: str, timeout: float = 8) -> None:
    wait_for_condition(
        driver,
        lambda d: expected.lower() in d.find_element(By.ID, "loadedModelName").text.lower(),
        timeout=timeout,
    )


def get_shape_class(driver: WebDriver) -> str:
    return driver.find_element(By.ID, "shape").get_attribute("class") or ""


def is_3d_visible(driver: WebDriver) -> bool:
    classes = driver.find_element(By.ID, "model3d").get_attribute("class") or ""
    return "hidden" not in classes
