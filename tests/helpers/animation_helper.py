"""Управление анимациями Motion Playground и чтение их состояния."""

from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from tests.helpers.browser_helper import js, wait_for_condition, wait_clickable

ANIMATION_KEYS = ("pulse", "rotate", "slide", "fade", "bounce")
SPEEDS = (0.5, 1.0, 2.0, 3.0)
BASE_DURATIONS_MS = {
    "pulse": 1200,
    "rotate": 3000,
    "slide": 2000,
    "fade": 1500,
    "bounce": 1500,
}


def select_animation(driver: WebDriver, key: str) -> None:
    wait_clickable(driver, By.ID, f"anim-{key}").click()


def start_animation(driver: WebDriver) -> None:
    wait_clickable(driver, By.ID, "startBtn").click()


def stop_animation(driver: WebDriver) -> None:
    wait_clickable(driver, By.ID, "stopBtn").click()


def set_animation_speed(driver: WebDriver, speed: float) -> None:
    js(
        driver,
        """
        const input = document.getElementById('speed');
        input.value = arguments[0];
        input.dispatchEvent(new Event('input', { bubbles: true }));
        """,
        str(speed),
    )


def set_combine(driver: WebDriver, enabled: bool) -> None:
    current = js(driver, "return document.getElementById('combine').checked;")
    if bool(current) != enabled:
        driver.find_element(By.ID, "combine").click()


def set_3d(driver: WebDriver, enabled: bool) -> None:
    current = js(driver, "return document.getElementById('use3d').checked;")
    if bool(current) != enabled:
        driver.find_element(By.ID, "use3d").click()


def get_motion_state(driver: WebDriver) -> dict:
    return js(driver, "return window.motionGetLocalState ? window.motionGetLocalState() : window.motionState;")


def get_running_animations_info(driver: WebDriver) -> list[dict]:
    return js(driver, "return window.motionGetAnimationsInfo ? window.motionGetAnimationsInfo() : [];")


def wait_for_animation_state(driver: WebDriver, playing: bool, timeout: float = 8) -> None:
    wait_for_condition(
        driver,
        lambda d: bool(get_motion_state(d).get("playing")) is playing,
        timeout=timeout,
    )


def wait_for_running_animations(driver: WebDriver, minimum: int = 1, timeout: float = 8) -> list[dict]:
    def _ready(d: WebDriver) -> list[dict] | bool:
        info = get_running_animations_info(d)
        return info if len(info) >= minimum else False

    return wait_for_condition(driver, _ready, timeout)


def get_computed_transform(driver: WebDriver, selector: str = "#actor") -> dict:
    return js(driver, "return window.motionGetComputedTransform(arguments[0]);", selector)


def get_element_bounds(driver: WebDriver, selector: str) -> dict:
    return js(
        driver,
        """
        const el = document.querySelector(arguments[0]);
        if (!el) return null;
        const rect = el.getBoundingClientRect();
        return {x: rect.x, y: rect.y, width: rect.width, height: rect.height, top: rect.top, left: rect.left};
        """,
        selector,
    )


def capture_model_screenshot(driver: WebDriver, path: str, selector: str = "#stage") -> str:
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.screenshot(path)
    return path


def compare_screenshots(path_a: str, path_b: str, tolerance: float = 0.08) -> dict:
    import numpy as np
    from PIL import Image

    first = np.asarray(Image.open(path_a).convert("RGB"), dtype=np.float32)
    second = np.asarray(Image.open(path_b).convert("RGB"), dtype=np.float32)
    if first.shape != second.shape:
        return {"similar": False, "reason": "size_mismatch", "diff": 1.0}
    diff = np.mean(np.abs(first - second) / 255.0)
    return {"similar": bool(diff <= tolerance), "diff": float(diff), "tolerance": tolerance}


def expected_cycle_ms(key: str, speed: float) -> float:
    return BASE_DURATIONS_MS[key] / max(0.1, speed)
