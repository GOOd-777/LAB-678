from __future__ import annotations

import pytest

from tests.helpers.metrics_helper import (
    Measurement,
    save_measurements,
)
from tests.helpers.chart_helper import plot_search_comparison


def _driver(animation_page):
    return animation_page.driver


def _measure_search(driver, kind: str, query: str) -> dict:
    """
    Измеряет реальный поиск внутри браузера.
    Дополнительно разбивает время на этапы.
    """

    return driver.execute_async_script("""
        const kind = arguments[0];
        const query = arguments[1];
        const done = arguments[arguments.length - 1];

        (async () => {
            const catalogGetter = kind === "background"
                ? window.getBackgroundCatalog
                : window.getScreensaverCatalog;

            const finder = kind === "background"
                ? window.findBackground
                : window.findScreensaver;

            const filter = window.filterCatalogItems;
            const check = window.checkImageAvailability;

            const apply = kind === "background"
                ? window.applyStageBackground
                : window.applyScreensaver;

            const started = performance.now();

            const result = await finder(query, {});
            const totalMs = performance.now() - started;

            const catalogStarted = performance.now();
            const catalog = await catalogGetter();
            const candidates = filter(catalog, query);
            const catalogMs = performance.now() - catalogStarted;

            const validationStarted = performance.now();

            const valid = await Promise.all(
                candidates.map(async item => {
                    if (!item?.url) return false;
                    return await check(item.url);
                })
            );

            const validationMs =
                performance.now() - validationStarted;

            const validItems = candidates.filter(
                (_, index) => valid[index]
            );

            const displayStarted = performance.now();

            if (validItems.length) {
                apply(validItems[0].url);
            }

            const displayMs = performance.now() - displayStarted;

            done({
                totalMs,
                catalogMs,
                validationMs,
                displayMs,
                candidates: candidates.length,
                validCount: validItems.length,
                resultCount: result ? result.length : 0,
                status: result ? "ok" : "not_found"
            });
        })().catch(error => {
            done({
                status: "error",
                error: String(error)
            });
        });
    """, kind, query)


def _append_measurements(rows, result, scenario, kind, users=1):
    if result.get("status") == "error":
        rows.append(
            Measurement(
                scenario=scenario,
                model_or_effect=kind,
                users=users,
                status="error",
                extras={"error": result.get("error")},
            )
        )
        return

    for stage in ("totalMs", "catalogMs", "validationMs", "displayMs"):
        rows.append(
            Measurement(
                scenario=f"{scenario}-{stage}",
                model_or_effect=kind,
                users=users,
                duration_ms=float(result.get(stage, 0)),
                status="ok",
                extras={
                    "candidates": result.get("candidates", 0),
                    "validCount": result.get("validCount", 0),
                },
            )
        )


@pytest.mark.student
@pytest.mark.performance
def test_measure_background_search_time(animation_page, reports_dir):
    driver = _driver(animation_page)
    rows = []

    for repetition in range(1, 6):
        result = _measure_search(driver, "background", "sunset")

        _append_measurements(
            rows,
            result,
            f"background-success-{repetition}",
            "background",
        )

    save_measurements(rows, "background-search.csv")

    successful = [
        row for row in rows
        if row.status == "ok"
        and row.scenario.endswith("totalMs")
    ]

    assert len(successful) == 5
    assert all(row.duration_ms > 0 for row in successful)


@pytest.mark.student
@pytest.mark.performance
def test_measure_screensaver_search_time(animation_page, reports_dir):
    driver = _driver(animation_page)
    rows = []

    for repetition in range(1, 6):
        result = _measure_search(driver, "screensaver", "aurora")

        _append_measurements(
            rows,
            result,
            f"screensaver-search-{repetition}",
            "screensaver",
        )

    save_measurements(rows, "screensaver-search.csv")

    successful = [
        row for row in rows
        if row.status == "ok"
        and row.scenario.endswith("totalMs")
    ]

    assert len(successful) == 5


@pytest.mark.student
@pytest.mark.performance
def test_compare_search_success_and_failure(animation_page, reports_dir):
    driver = _driver(animation_page)
    rows = []

    scenarios = [
        ("success", "sunset"),
        ("failure", "nonexistent_background_123456"),
    ]

    for scenario, query in scenarios:
        for repetition in range(5):
            result = _measure_search(driver, "background", query)

            _append_measurements(
                rows,
                result,
                f"{scenario}-{repetition + 1}",
                "background",
            )

    save_measurements(rows, "search-success-failure.csv")

    plot_search_comparison(
        rows,
        prefix="search-success-failure",
    )

    assert any("success" in row.scenario for row in rows)
    assert any("failure" in row.scenario for row in rows)


@pytest.mark.student
@pytest.mark.performance
def test_search_under_active_effects(animation_page, reports_dir):
    driver = _driver(animation_page)
    rows = []

    # Проверяем состояние анимаций, не изменяя настройки приложения.
    animations = driver.execute_script("""
        return window.motionGetAnimationsInfo
            ? window.motionGetAnimationsInfo()
            : [];
    """)

    animation_count = len(animations)

    for repetition in range(5):
        result = _measure_search(driver, "background", "sunset")

        _append_measurements(
            rows,
            result,
            f"search-with-{animation_count}-active-animations-{repetition + 1}",
            "current-effects",
        )

    # Дополнительно сохраняем информацию об анимациях.
    for row in rows:
        row.extras["activeAnimations"] = animation_count

    save_measurements(rows, "search-active-effects.csv")

    assert rows
    assert any(row.status == "ok" for row in rows)


@pytest.mark.student
@pytest.mark.performance
def test_search_time_by_users_and_charts(
    isolated_room,
    animation_page,
    reports_dir,
):
    driver = _driver(animation_page)
    rows = []

    # Число параллельных поисковых операций моделирует нагрузку
    # от нескольких пользователей.
    user_counts = [1, 2, 5, 10]

    for users in user_counts:
        for repetition in range(3):

            result = driver.execute_async_script("""
                const users = arguments[0];
                const done = arguments[arguments.length - 1];

                const started = performance.now();

                Promise.all(
                    Array.from(
                        { length: users },
                        () => window.findBackground("sunset", {})
                    )
                ).then(results => {
                    done({
                        durationMs: performance.now() - started,
                        count: results.filter(Boolean).length,
                        status: "ok"
                    });
                }).catch(error => {
                    done({
                        status: "error",
                        error: String(error)
                    });
                });
            """, users)

            rows.append(
                Measurement(
                    scenario=f"concurrent-search-{users}-users",
                    model_or_effect="background",
                    users=users,
                    repetition=repetition + 1,
                    duration_ms=float(result.get("durationMs", 0)),
                    status=result.get("status", "error"),
                    extras={
                        "successfulRequests": result.get("count", 0),
                        "error": result.get("error"),
                    },
                )
            )

    save_measurements(rows, "search-users.csv")

    # График сравнения всех сценариев.
    paths = plot_search_comparison(
        rows,
        prefix="background-search-users",
    )

    assert len(rows) == 12
    assert paths
    assert all(path.exists() for path in paths)