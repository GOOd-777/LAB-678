"""Построение PNG-графиков по фактическим измерениям."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

from tests.helpers.metrics_helper import Measurement, REPORTS, calculate_statistics


def _prepare(path: str | Path) -> Path:
    REPORTS.mkdir(parents=True, exist_ok=True)
    target = Path(path)
    if not target.is_absolute():
        target = REPORTS / target
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def plot_comparison(
    labels: list[str],
    values: list[float],
    title: str,
    xlabel: str,
    ylabel: str,
    filename: str,
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    target = _prepare(filename)
    figure, axes = plt.subplots(figsize=(8, 4.5))
    axes.bar(labels, values, color="#38bdf8")
    axes.set_title(title)
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.tick_params(axis="x", rotation=20)
    figure.tight_layout()
    figure.savefig(target, dpi=120)
    plt.close(figure)
    return target


def plot_grouped_bars(
    series: dict[str, list[float]],
    categories: list[str],
    title: str,
    ylabel: str,
    filename: str,
) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    target = _prepare(filename)
    x = np.arange(len(categories))
    width = 0.8 / max(1, len(series))
    figure, axes = plt.subplots(figsize=(9, 4.8))
    for index, (name, values) in enumerate(series.items()):
        axes.bar(x + index * width, values, width, label=name)
    axes.set_xticks(x + width * (len(series) - 1) / 2)
    axes.set_xticklabels(categories)
    axes.set_title(title)
    axes.set_ylabel(ylabel)
    axes.legend()
    figure.tight_layout()
    figure.savefig(target, dpi=120)
    plt.close(figure)
    return target


def plot_animation_cycle_comparison(rows: Iterable[Measurement], prefix: str = "animation-cycle") -> list[Path]:
    by_effect: dict[str, list[float]] = defaultdict(list)
    by_speed: dict[str, list[float]] = defaultdict(list)
    single: list[float] = []
    combined: list[float] = []
    for row in rows:
        if row.status != "ok":
            continue
        by_effect[row.model_or_effect or "unknown"].append(row.duration_ms)
        if row.speed is not None:
            by_speed[str(row.speed)].append(row.duration_ms)
        if "combine" in row.scenario:
            combined.append(row.duration_ms)
        else:
            single.append(row.duration_ms)

    paths = [
        plot_comparison(
            list(by_effect),
            [calculate_statistics(values)["median"] for values in by_effect.values()],
            "Длительность цикла по эффектам",
            "Эффект",
            "Медиана, мс",
            f"{prefix}-by-effect.png",
        ),
        plot_comparison(
            list(by_speed),
            [calculate_statistics(values)["median"] for values in by_speed.values()],
            "Длительность цикла от скорости",
            "Скорость",
            "Медиана, мс",
            f"{prefix}-by-speed.png",
        ),
        plot_comparison(
            ["Одиночные", "Комбинированные"],
            [
                calculate_statistics(single)["median"] if single else 0.0,
                calculate_statistics(combined)["median"] if combined else 0.0,
            ],
            "Одиночные и комбинированные эффекты",
            "Тип",
            "Медиана, мс",
            f"{prefix}-single-vs-combined.png",
        ),
    ]
    return paths


def plot_session_scalability(rows: Iterable[Measurement], prefix: str = "session") -> list[Path]:
    by_users_latency: dict[int, list[float]] = defaultdict(list)
    by_users_errors: dict[int, list[int]] = defaultdict(list)
    by_users_throughput: dict[int, list[float]] = defaultdict(list)
    sse: dict[int, list[float]] = defaultdict(list)
    for row in rows:
        users = int(row.users or 0)
        if "sse" in row.scenario:
            sse[users].append(row.duration_ms)
        elif "throughput" in row.scenario:
            by_users_throughput[users].append(row.duration_ms)
        else:
            by_users_latency[users].append(row.duration_ms)
        by_users_errors[users].append(0 if row.status == "ok" else 1)

    def _median_map(mapping: dict[int, list[float]]) -> tuple[list[str], list[float]]:
        keys = sorted(mapping)
        return [str(key) for key in keys], [calculate_statistics(mapping[key])["median"] for key in keys]

    labels, latency = _median_map(by_users_latency)
    t_labels, throughput = _median_map(by_users_throughput)
    e_labels = [str(key) for key in sorted(by_users_errors)]
    errors = [
        100.0 * (sum(by_users_errors[key]) / max(1, len(by_users_errors[key])))
        for key in sorted(by_users_errors)
    ]
    s_labels, sse_values = _median_map(sse)
    return [
        plot_comparison(labels, latency, "Latency от числа пользователей", "Пользователи", "мс", f"{prefix}-latency.png"),
        plot_comparison(t_labels, throughput, "Throughput от числа пользователей", "Пользователи", "опер/с", f"{prefix}-throughput.png"),
        plot_comparison(e_labels, errors, "Error rate от числа пользователей", "Пользователи", "%", f"{prefix}-errors.png"),
        plot_comparison(s_labels, sse_values, "Задержка SSE от числа пользователей", "Пользователи", "мс", f"{prefix}-sse.png"),
    ]


def plot_download_comparison(rows: Iterable[Measurement], prefix: str = "download") -> list[Path]:
    by_source: dict[str, list[float]] = defaultdict(list)
    throughput: dict[str, list[float]] = defaultdict(list)
    cache: dict[str, list[float]] = defaultdict(list)
    delayed: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        if row.status != "ok":
            continue
        by_source[row.source or "unknown"].append(row.duration_ms)
        if "throughput_bps" in (row.extras or {}):
            throughput[row.source or "unknown"].append(float(row.extras["throughput_bps"]))
        if "cache" in row.scenario:
            cache[row.scenario].append(row.duration_ms)
        if "delay" in (row.source or "") or "delay" in row.scenario:
            delayed[row.source or row.scenario].append(row.duration_ms)
    paths = [
        plot_comparison(
            list(by_source),
            [calculate_statistics(values)["median"] for values in by_source.values()],
            "Время скачивания по источникам",
            "Источник",
            "мс",
            f"{prefix}-duration.png",
        )
    ]
    if throughput:
        paths.append(
            plot_comparison(
                list(throughput),
                [calculate_statistics(values)["median"] for values in throughput.values()],
                "Throughput по источникам",
                "Источник",
                "байт/с",
                f"{prefix}-throughput.png",
            )
        )
    if cache:
        paths.append(
            plot_comparison(
                list(cache),
                [calculate_statistics(values)["median"] for values in cache.values()],
                "Холодный и тёплый кеш",
                "Сценарий",
                "мс",
                f"{prefix}-cache.png",
            )
        )
    if delayed:
        paths.append(
            plot_comparison(
                list(delayed),
                [calculate_statistics(values)["median"] for values in delayed.values()],
                "Влияние задержки",
                "Источник",
                "мс",
                f"{prefix}-delay.png",
            )
        )
    return paths


def plot_search_comparison(rows: Iterable[Measurement], prefix: str = "search") -> list[Path]:
    groups = defaultdict(list)
    for row in rows:
        if row.status != "ok":
            continue
        groups[row.scenario].append(row.duration_ms)
    return [
        plot_comparison(
            list(groups),
            [calculate_statistics(values)["median"] for values in groups.values()],
            "Сравнение времени поиска",
            "Сценарий",
            "мс",
            f"{prefix}-comparison.png",
        )
    ]


def plot_demo_chart(filename: str = "demo-chart.png") -> Path:
    """Демонстрационный график на заранее обозначенном наборе данных, не на живых измерениях."""
    return plot_comparison(
        ["A", "B", "C"],
        [10, 20, 15],
        "DEMO DATA: не является результатом лабораторного измерения",
        "Категория",
        "Значение",
        filename,
    )
