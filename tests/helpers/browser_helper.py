"""Запуск Selenium и ожидание состояний без фиксированных sleep()."""

from __future__ import annotations

import os
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from selenium.webdriver import Chrome, Remote
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".selenium-cache"


def _find_chromedriver() -> Path | None:
    root = CACHE / "chromedriver" / "linux64"
    if not root.exists():
        return None
    matches = sorted(root.glob("*/chromedriver"))
    return matches[-1] if matches else None


def chrome_options(headless: bool = True, window_size: str = "1280,800") -> Options:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    profile = tempfile.mkdtemp(prefix="mpw-chrome-")
    options.add_argument(f"--user-data-dir={profile}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-extensions")
    options.add_argument(f"--window-size={window_size}")
    options.add_argument("--lang=ru-RU")
    for candidate in ("/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium-browser"):
        if Path(candidate).exists():
            options.binary_location = candidate
            break
    return options


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def create_driver(headless: bool = True, window_size: str = "1280,800") -> WebDriver:
    CACHE.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("SE_CACHE_PATH", str(CACHE))
    os.environ.setdefault("SE_AVOID_STATS", "true")
    options = chrome_options(headless=headless, window_size=window_size)
    driver_path = _find_chromedriver()

    # Надёжный путь для окружений, где Chrome() через Service зависает:
    # поднимаем chromedriver сами и подключаемся через Remote.
    if driver_path and driver_path.exists():
        port = _free_port()
        process = subprocess.Popen(
            [str(driver_path), f"--port={port}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 10
        while time.time() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                    break
            except OSError:
                if process.poll() is not None:
                    break
                time.sleep(0.05)
        else:
            process.kill()
            raise RuntimeError("ChromeDriver did not start")

        driver = Remote(command_executor=f"http://127.0.0.1:{port}", options=options)
        driver._mpw_chromedriver_process = process  # type: ignore[attr-defined]
        driver.set_page_load_timeout(20)
        driver.set_script_timeout(15)
        return driver

    driver = Chrome(options=options, service=Service())
    driver.set_page_load_timeout(20)
    driver.set_script_timeout(15)
    return driver


def quit_driver(driver: WebDriver) -> None:
    process = getattr(driver, "_mpw_chromedriver_process", None)
    try:
        driver.quit()
    except Exception:
        pass
    if process is not None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except Exception:
            process.kill()


def wait(driver: WebDriver, timeout: float = 8) -> WebDriverWait:
    return WebDriverWait(driver, timeout)


def wait_visible(driver: WebDriver, by: str, value: str, timeout: float = 8) -> WebElement:
    return wait(driver, timeout).until(EC.visibility_of_element_located((by, value)))


def wait_clickable(driver: WebDriver, by: str, value: str, timeout: float = 8) -> WebElement:
    return wait(driver, timeout).until(EC.element_to_be_clickable((by, value)))


def wait_for_condition(driver: WebDriver, predicate: Callable[[WebDriver], Any], timeout: float = 8):
    return wait(driver, timeout).until(predicate)


def js(driver: WebDriver, script: str, *args):
    return driver.execute_script(script, *args)


def set_window_size(driver: WebDriver, width: int, height: int) -> None:
    driver.set_window_size(width, height)


def show_local_actor(driver: WebDriver) -> None:
    js(driver, "document.body.classList.add('lab-show-local-actor');")


def hide_local_actor(driver: WebDriver) -> None:
    js(driver, "document.body.classList.remove('lab-show-local-actor');")


def wait_document_ready(driver: WebDriver, timeout: float = 8) -> None:
    wait_for_condition(driver, lambda d: js(d, "return document.readyState") == "complete", timeout)


def find(driver: WebDriver, element_id: str) -> WebElement:
    return driver.find_element(By.ID, element_id)
