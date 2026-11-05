#!/usr/bin/env python3
"""Собирает независимые Git-патчи эталонных решений относительно студенческой версии."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "instructor_solutions" / "_src"
OUT = ROOT / "instructor_solutions"
TMP = ROOT / ".patch-build"


def run(cmd: list[str], cwd: Path) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True)


def replace_function(text: str, name: str, new_body: str) -> str:
    start = text.index(f"async function {name}(")
    end = text.index("\n  }", start) + len("\n  }")
    return text[:start] + new_body.strip() + text[end:]


def write_student_api(target: Path, load_model: bool = False, search: bool = False) -> None:
    text = (ROOT / "student_api.js").read_text(encoding="utf-8")
    if load_model:
        body = (SRC / "01" / "loadModel.js").read_text(encoding="utf-8")
        text = replace_function(text, "loadModel", body)
    if search:
        bodies = (SRC / "07" / "search.js").read_text(encoding="utf-8")
        text = replace_function(text, "findBackground", bodies.split("async function findScreensaver")[0])
        text = replace_function(text, "findScreensaver", "async function findScreensaver" + bodies.split("async function findScreensaver")[1])
    target.write_text(text, encoding="utf-8")


def write_metrics_helper_with_cycle(target: Path) -> None:
    text = (ROOT / "tests" / "helpers" / "metrics_helper.py").read_text(encoding="utf-8")
    body = (SRC / "04" / "measure_animation_cycle.py").read_text(encoding="utf-8").rstrip() + "\n\n\n"
    start = text.index("def measure_animation_cycle(")
    end = text.index("\ndef collect_cycle_measurements(")
    target.write_text(text[:start] + body + text[end:], encoding="utf-8")


PATCHES = [
    {
        "name": "01-model-loading.patch",
        "files": {
            "student_api.js": lambda dest: write_student_api(dest, load_model=True),
            "tests/ui/test_model_loading_ui.py": SRC / "01" / "test_model_loading_ui.py",
            "tests/e2e/test_model_loading_e2e.py": SRC / "01" / "test_model_loading_e2e.py",
        },
    },
    {
        "name": "02-combined-effects.patch",
        "files": {"tests/e2e/test_combined_effects.py": SRC / "02" / "test_combined_effects.py"},
    },
    {
        "name": "03-rendering-2d-3d.patch",
        "files": {"tests/ui/test_rendering_2d_3d.py": SRC / "03" / "test_rendering_2d_3d.py"},
    },
    {
        "name": "04-animation-cycle.patch",
        "files": {
            "tests/helpers/metrics_helper.py": write_metrics_helper_with_cycle,
            "tests/performance/test_animation_cycle.py": SRC / "04" / "test_animation_cycle.py",
        },
    },
    {
        "name": "05-session-performance.patch",
        "files": {"tests/performance/test_session_scalability.py": SRC / "05" / "test_session_scalability.py"},
    },
    {
        "name": "06-event-observability.patch",
        "files": {"tests/observability/test_event_observability.py": SRC / "06" / "test_event_observability.py"},
    },
    {
        "name": "07-background-search.patch",
        "files": {
            "student_api.js": lambda dest: write_student_api(dest, search=True),
            "tests/ui/test_background_search_ui.py": SRC / "07" / "test_background_search_ui.py",
            "tests/performance/test_background_search.py": SRC / "07" / "test_background_search.py",
        },
    },
    {
        "name": "08-download-performance.patch",
        "files": {"tests/performance/test_download_sources.py": SRC / "08" / "test_download_sources.py"},
    },
]


def copy_tree() -> Path:
    if TMP.exists():
        shutil.rmtree(TMP)
    TMP.mkdir()
    base = TMP / "base"
    shutil.copytree(
        ROOT,
        base,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            ".selenium-cache",
            ".patch-build",
            "instructor_solutions",
            "reports",
            "__pycache__",
            ".pytest_cache",
        ),
    )
    (base / "reports").mkdir()
    (base / "reports" / ".gitkeep").write_text("")
    run(["git", "init"], base)
    run(["git", "add", "-A"], base)
    run(["git", "-c", "user.email=lab@example.com", "-c", "user.name=Lab", "commit", "-m", "student base"], base)
    return base


def build_patch(base: Path, spec: dict) -> None:
    work = TMP / spec["name"].replace(".patch", "")
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(base, work, ignore=shutil.ignore_patterns(".git"))
    shutil.copytree(base / ".git", work / ".git")
    for relative, source in spec["files"].items():
        dest = work / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if callable(source):
            source(dest)
        else:
            shutil.copyfile(source, dest)
    diff = run(["git", "diff", "--binary"], work)
    if not diff.strip():
        raise RuntimeError(f"Empty patch for {spec['name']}")
    (OUT / spec["name"]).write_text(diff, encoding="utf-8")
    print(f"wrote {spec['name']} ({len(diff.splitlines())} lines)")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    base = copy_tree()
    for spec in PATCHES:
        build_patch(base, spec)
    shutil.rmtree(TMP)
    print("done")


if __name__ == "__main__":
    main()
