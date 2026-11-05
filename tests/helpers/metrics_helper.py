"""Измерение времени, статистика и сохранение CSV."""

from __future__ import annotations

import csv
import json
import platform
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

from selenium.webdriver.remote.webdriver import WebDriver

from tests.helpers.browser_helper import js
from tests.helpers.animation_helper import get_running_animations_info, wait_for_running_animations

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports"


@dataclass
class Measurement:
    scenario: str
    model_or_effect: str = ""
    source: str = ""
    speed: float | None = None
    users: int | None = None
    repetition: int = 1
    duration_ms: float = 0.0
    status: str = "ok"
    extras: dict[str, Any] = field(default_factory=dict)


def measure_duration(operation: Callable[[], Any]) -> tuple[Any, float]:
    started = time.perf_counter()
    result = operation()
    return result, (time.perf_counter() - started) * 1000.0


def collect_measurements(
    operation: Callable[[], Any],
    repeats: int,
    scenario: str,
    **fields: Any,
) -> list[Measurement]:
    rows: list[Measurement] = []
    for index in range(1, repeats + 1):
        try:
            _result, duration_ms = measure_duration(operation)
            status = "ok"
        except Exception as exc:  # noqa: BLE001 — измеряем и ошибки
            duration_ms = 0.0
            status = f"error:{exc.__class__.__name__}"
        rows.append(
            Measurement(
                scenario=scenario,
                repetition=index,
                duration_ms=duration_ms,
                status=status,
                **{key: value for key, value in fields.items() if key in Measurement.__dataclass_fields__},
            )
        )
        if rows[-1].extras is None:
            rows[-1].extras = {}
        extra_fields = {key: value for key, value in fields.items() if key not in Measurement.__dataclass_fields__}
        if extra_fields:
            rows[-1].extras.update(extra_fields)
    return rows


def calculate_statistics(values: Iterable[float]) -> dict[str, float]:
    data = [float(item) for item in values]
    if not data:
        return {"count": 0, "mean": 0.0, "median": 0.0, "p95": 0.0, "stdev": 0.0, "min": 0.0, "max": 0.0}
    ordered = sorted(data)
    p95_index = min(len(ordered) - 1, max(0, int(round(0.95 * (len(ordered) - 1)))))
    return {
        "count": len(ordered),
        "mean": statistics.fmean(ordered),
        "median": statistics.median(ordered),
        "p95": ordered[p95_index],
        "stdev": statistics.pstdev(ordered) if len(ordered) > 1 else 0.0,
        "min": ordered[0],
        "max": ordered[-1],
    }


def capture_environment(**extra: Any) -> dict[str, Any]:
    payload = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        **extra,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "environment.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def save_measurements(rows: list[Measurement], filename: str) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / filename
    fieldnames = [
        "scenario",
        "model_or_effect",
        "source",
        "speed",
        "users",
        "repetition",
        "duration_ms",
        "status",
        "extras",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            payload = asdict(row)
            payload["extras"] = json.dumps(payload.get("extras") or {}, ensure_ascii=False)
            writer.writerow(payload)
    return path


def measure_animation_cycle(driver: WebDriver, effect_index: int = 0) -> dict[str, float]:
    """Измеряет одну итерацию уже запущенной анимации.

    Функциональные требования:
    - Анимация уже запущена; запуск браузера в измерение не входит.
    - Измерить длительность одного цикла анимации с индексом effect_index.
    - Вернуть словарь с фактической длительностью (durationMs) и служебными полями
      (например configuredMs, effectIndex).
    - Не использовать фиксированный sleep() как способ «дождаться конца цикла».

    Подсказки:
    - Дождаться появления анимаций: wait_for_running_animations, get_running_animations_info.
    - В браузере удобны Web Animations API и performance.now()
      (через driver.execute_async_script).
    """
    # TODO: Реализовать измерение одного цикла анимации.
    raise NotImplementedError("TODO: implement measure_animation_cycle")


def collect_cycle_measurements(
    driver: WebDriver,
    repeats: int,
    scenario: str,
    effect: str,
    speed: float,
    effect_index: int = 0,
) -> list[Measurement]:
    rows: list[Measurement] = []
    for index in range(1, repeats + 1):
        sample = measure_animation_cycle(driver, effect_index=effect_index)
        rows.append(
            Measurement(
                scenario=scenario,
                model_or_effect=effect,
                speed=speed,
                repetition=index,
                duration_ms=float(sample.get("durationMs") or 0.0),
                status="ok" if "durationMs" in sample else "error",
                extras={"configuredMs": sample.get("configuredMs")},
            )
        )
    return rows
