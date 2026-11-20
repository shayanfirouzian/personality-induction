#!/usr/bin/env python3
"""Regenerate the static supplementary figures from repository records.

Run from the repository root:
    python scripts/reproduce_figures.py

Requires Matplotlib; all input data are read from the checked-in CSV/JSON files.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

PROFILES = ["LLL", "LLH", "LHL", "LHH", "HLL", "HLH", "HHL", "HHH"]
TRAITS = ["Extraversion", "Neuroticism", "Openness"]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Required input file not found: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


def dpo_figure(root: Path) -> None:
    rows = read_csv(root / "data/dpo/dpo_evaluation_metrics.csv")
    steps = [int(r["step"]) for r in rows]
    series = [
        ("Validation loss", [float(r["validation_loss"]) for r in rows]),
        ("Reward accuracy", [float(r["rewards_accuracy"]) for r in rows]),
        ("Reward margin", [float(r["rewards_margin"]) for r in rows]),
    ]
    fig, axes = plt.subplots(3, 1, figsize=(8.2, 8.4), sharex=True)
    for ax, (label, values) in zip(axes, series):
        ax.plot(steps, values, marker="o", linewidth=1.5)
        ax.set_ylabel(label)
        ax.grid(True, alpha=0.25)
    axes[-1].set_xlabel("Training step")
    save(fig, root / "figures/dpo_training_metrics.png")


def hpo_figure(root: Path, stage: str) -> None:
    if stage == "surrogate":
        rows = read_csv(root / "data/hpo/surrogate_trials.csv")
        objective = "minimum_logged_validation_loss"
        title = "Surrogate-task HPO: retained trial results"
        path = root / "figures/surrogate_hpo_history.png"
    else:
        rows = read_csv(root / "data/hpo/main_trials.csv")
        objective = "validation_loss"
        title = "Main-task HPO: retained trial results"
        path = root / "figures/main_hpo_history.png"
    trials = [int(r.get("trial_id", r.get("trial", i + 1))) for i, r in enumerate(rows)]
    values = [float(r[objective]) for r in rows]
    best = np.minimum.accumulate(values)
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    ax.scatter(trials, values, label="Trial objective")
    ax.step(trials, best, where="mid", label="Best-so-far", linewidth=1.7)
    ax.set_title(title)
    ax.set_xlabel("Trial ID")
    ax.set_ylabel("Validation loss")
    ax.grid(True, alpha=0.25)
    ax.legend()
    save(fig, path)


def sft_figure(root: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    for profile in PROFILES:
        path = root / "data/sft/logs" / f"{profile}.json"
        if not path.exists():
            raise FileNotFoundError(f"Missing SFT log for profile {profile}: {path}")
        data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        history = data.get("log_history", [])
        points = [(int(row["step"]), float(row["eval_loss"]))
                  for row in history if "step" in row and "eval_loss" in row]
        if not points:
            raise ValueError(f"No evaluation-loss history found in {path}")
        points.sort(key=lambda item: item[0])
        ax.plot([x for x, _ in points], [y for _, y in points], marker=".", label=profile)
    ax.set_title("Profile-specific SFT validation-loss trajectories")
    ax.set_xlabel("Training step")
    ax.set_ylabel("Validation loss")
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=4, fontsize=8)
    save(fig, root / "figures/sft_validation_curves.png")


def calibration_figure(root: Path) -> None:
    rows = read_csv(root / "data/personality_assessment/calibration_distributions.csv")
    ratings = [int(r["rating"]) for r in rows]
    baseline = [int(r["baseline_count"]) for r in rows]
    deliberation = [int(r["deliberation_count"]) for r in rows]
    x = np.arange(len(ratings))
    width = 0.36
    fig, ax = plt.subplots(figsize=(7.6, 4.5))
    ax.bar(x - width / 2, baseline, width, label="Baseline prompt")
    ax.bar(x + width / 2, deliberation, width, label="Deliberation prompt")
    ax.set_xticks(x, [str(v) for v in ratings])
    ax.set_xlabel("Likert response")
    ax.set_ylabel("Frequency")
    ax.set_title("Baseline and deliberation response distributions")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    save(fig, root / "figures/prompt_calibration_distributions.png")


def profile_space_figure(root: Path) -> None:
    rows = read_csv(root / "data/personality_assessment/trait_scores_long.csv")
    fig = plt.figure(figsize=(8.0, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    for profile in PROFILES:
        group = [r for r in rows if r["profile"] == profile]
        if not group:
            raise ValueError(f"No assessment scores found for profile {profile}")
        ax.scatter(
            [float(r["Extraversion"]) for r in group],
            [float(r["Neuroticism"]) for r in group],
            [float(r["Openness"]) for r in group],
            label=profile,
            s=24,
        )
        ax.scatter(
            [sum(float(r["Extraversion"]) for r in group) / len(group)],
            [sum(float(r["Neuroticism"]) for r in group) / len(group)],
            [sum(float(r["Openness"]) for r in group) / len(group)],
            marker="X",
            s=65,
        )
    ax.set_xlabel("Extraversion")
    ax.set_ylabel("Neuroticism")
    ax.set_zlabel("Openness")
    ax.set_title("Eight induced profiles in three-trait score space")
    ax.legend(fontsize=8, ncol=2)
    save(fig, root / "figures/profile_trait_space.png")


def confusion_figure(root: Path) -> None:
    rows = read_csv(root / "derived/confusion_matrix.csv")
    profiles = [r["true_profile"] for r in rows]
    matrix = np.asarray([[int(r[p]) for p in profiles] for r in rows], dtype=int)
    fig, ax = plt.subplots(figsize=(7.2, 6.1))
    image = ax.imshow(matrix, interpolation="nearest", aspect="auto")
    ax.set_xticks(np.arange(len(profiles)), profiles, rotation=45, ha="right")
    ax.set_yticks(np.arange(len(profiles)), profiles)
    ax.set_xlabel("Predicted profile")
    ax.set_ylabel("True profile")
    ax.set_title("Confusion matrix (threshold-selected; n = 80)")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    save(fig, root / "figures/profile_confusion_matrix.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / "README.md").exists():
        raise SystemExit(f"{root} does not look like the repository root (README.md not found)")
    dpo_figure(root)
    hpo_figure(root, "surrogate")
    hpo_figure(root, "main")
    sft_figure(root)
    calibration_figure(root)
    profile_space_figure(root)
    confusion_figure(root)


if __name__ == "__main__":
    main()
