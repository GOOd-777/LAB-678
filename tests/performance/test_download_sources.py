
"""Лабораторная 8. Сравнение скорости скачивания из разных источников."""

from __future__ import annotations

import requests
import pytest

from tests.helpers.network_helper import (
    measure_download,
    download_measurement,
    calculate_throughput,
)
from tests.helpers.metrics_helper import (
    Measurement,
    save_measurements,
)
from tests.helpers.chart_helper import plot_download_comparison


EXPECTED_BYTES = 256 * 1024


def _download_urls(lab_config):
    return lab_config["downloads"]


def _save_and_plot(rows, filename, prefix):
    """Сохраняет измерения и строит графики."""
    save_measurements(rows, filename)
    return plot_download_comparison(rows, prefix=prefix)


@pytest.mark.student
@pytest.mark.performance
def test_download_from_all_sources(lab_config, reports_dir):
    """Сравнение загрузки файла из четырёх источников."""

    urls = _download_urls(lab_config)

    sources = {
        "local": urls["local"],
        "cdn": urls["cdn"],
        "delayed": urls["delayed"],
        "throttle": urls["throttle"],
    }

    rows = []

    for source, url in sources.items():
        for repetition in range(1, 3):
            row = download_measurement(
                url,
                scenario=f"download-{source}",
                source=source,
                repetition=repetition,
                expected_bytes=EXPECTED_BYTES,
                timeout=15,
            )

            rows.append(row)

            assert row.status == "ok", (
                f"{source}: загрузка завершилась со статусом "
                f"{row.status}"
            )

            assert row.extras["bytes"] == EXPECTED_BYTES
            assert row.extras["complete"] is True

            assert row.duration_ms > 0
            assert row.extras["throughput_bps"] > 0

    _save_and_plot(
        rows,
        "download-sources.csv",
        "download-sources",
    )

    assert len(rows) == 8


@pytest.mark.student
@pytest.mark.performance
def test_download_error_status(lab_config, reports_dir):
    """Проверка обработки HTTP-ошибки."""

    url = lab_config["downloads"]["errors"]

    result = measure_download(
        url,
        timeout=5,
        expected_bytes=EXPECTED_BYTES,
    )

    assert result["status"] == "http_503"
    assert result["complete"] is False

    row = download_measurement(
        url,
        scenario="download-http-error",
        source="errors",
        expected_bytes=EXPECTED_BYTES,
    )

    assert row.status == "http_503"

    save_measurements(
        [row],
        "download-errors.csv",
    )


@pytest.mark.student
@pytest.mark.performance
def test_download_timeout(lab_config, reports_dir):
    """Проверка тайм-аута при медленном источнике."""

    url = lab_config["downloads"]["delayed"]

    result = measure_download(
        url,
        timeout=0.05,
        expected_bytes=EXPECTED_BYTES,
    )

    assert result["status"] == "timeout"
    assert result["complete"] is False

    row = Measurement(
        scenario="download-timeout",
        source="delayed",
        duration_ms=result["duration_ms"],
        status=result["status"],
        extras={
            "bytes": result["bytes"],
            "complete": result["complete"],
        },
    )

    save_measurements(
        [row],
        "download-timeout.csv",
    )


@pytest.mark.student
@pytest.mark.performance
def test_download_incomplete(lab_config, reports_dir):
    """Проверка неполной загрузки файла."""

    url = lab_config["downloads"]["incomplete"]

    result = measure_download(
        url,
        timeout=5,
        expected_bytes=EXPECTED_BYTES,
    )

    assert result["status"] == "incomplete"
    assert result["complete"] is False
    assert result["bytes"] < EXPECTED_BYTES

    row = Measurement(
        scenario="download-incomplete",
        source="incomplete",
        duration_ms=result["duration_ms"],
        status=result["status"],
        extras={
            "bytes": result["bytes"],
            "expected_bytes": EXPECTED_BYTES,
            "complete": result["complete"],
        },
    )

    save_measurements(
        [row],
        "download-incomplete.csv",
    )


@pytest.mark.student
@pytest.mark.performance
def test_compare_cold_and_warm_download(
    lab_config,
    reports_dir,
):
    """Сравнение первого и повторного запроса через одну Session."""

    url = lab_config["downloads"]["local"]

    session = requests.Session()
    rows = []

    try:
        for repetition, scenario in enumerate(
            ["cold-connection", "warm-connection"],
            start=1,
        ):
            row = download_measurement(
                url,
                scenario=scenario,
                source="local-cache",
                repetition=repetition,
                expected_bytes=EXPECTED_BYTES,
                timeout=10,
                session=session,
            )

            assert row.status == "ok"
            assert row.extras["bytes"] == EXPECTED_BYTES

            rows.append(row)

    finally:
        session.close()

    assert len(rows) == 2

    save_measurements(
        rows,
        "download-cache.csv",
    )

    # Не требуем, чтобы повторный запрос обязательно был быстрее:
    # на результат влияют сеть и нагрузка сервера.


@pytest.mark.student
@pytest.mark.performance
def test_compare_cdn_cache_headers(
    lab_config,
    reports_dir,
):
    """Сравнение заголовков кеширования CDN и локального источника."""

    urls = lab_config["downloads"]

    local = measure_download(
        urls["local"],
        expected_bytes=EXPECTED_BYTES,
    )

    cdn = measure_download(
        urls["cdn"],
        expected_bytes=EXPECTED_BYTES,
    )

    assert local["status"] == "ok"
    assert cdn["status"] == "ok"

    local_cache = local["headers"].get("X-Cache")
    cdn_cache = cdn["headers"].get("X-Cache")

    assert cdn_cache == "HIT"

    rows = [
        Measurement(
            scenario="local-cache-header",
            source="local",
            duration_ms=local["duration_ms"],
            status=local["status"],
            extras={
                "x_cache": local_cache,
                "bytes": local["bytes"],
            },
        ),
        Measurement(
            scenario="cdn-cache-header",
            source="cdn",
            duration_ms=cdn["duration_ms"],
            status=cdn["status"],
            extras={
                "x_cache": cdn_cache,
                "bytes": cdn["bytes"],
            },
        ),
    ]

    save_measurements(
        rows,
        "download-cdn-cache.csv",
    )


@pytest.mark.student
@pytest.mark.performance
def test_download_throughput(
    lab_config,
    reports_dir,
):
    """Проверка расчёта пропускной способности."""

    urls = lab_config["downloads"]

    rows = []

    for source in ["local", "cdn", "delayed", "throttle"]:
        result = measure_download(
            urls[source],
            timeout=15,
            expected_bytes=EXPECTED_BYTES,
        )

        assert result["status"] == "ok"

        throughput = calculate_throughput(
            result["bytes"],
            result["duration_ms"],
        )

        assert throughput > 0

        rows.append(
            Measurement(
                scenario=f"throughput-{source}",
                source=source,
                duration_ms=result["duration_ms"],
                status=result["status"],
                extras={
                    "bytes": result["bytes"],
                    "throughput_bps": throughput,
                },
            )
        )

    paths = _save_and_plot(
        rows,
        "download-throughput.csv",
        "download-throughput",
    )

    assert paths
    assert all(path.exists() for path in paths)


@pytest.mark.student
@pytest.mark.performance
def test_generate_download_reports(
    lab_config,
    reports_dir,
):
    """Итоговое сравнение источников и построение графиков."""

    urls = lab_config["downloads"]

    rows = []

    for source in ["local", "cdn", "delayed", "throttle"]:
        for repetition in range(1, 4):
            row = download_measurement(
                urls[source],
                scenario=f"download-{source}",
                source=source,
                repetition=repetition,
                expected_bytes=EXPECTED_BYTES,
                timeout=15,
            )

            rows.append(row)

    assert len(rows) == 12

    successful = [row for row in rows if row.status == "ok"]

    assert len(successful) == 12

    paths = _save_and_plot(
        rows,
        "download-final.csv",
        "download-final",
    )

    assert paths
    assert all(path.exists() for path in paths)
