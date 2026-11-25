"""Validate run labels without treating unclassified runs as negative cases."""
from __future__ import annotations

import csv
from pathlib import Path


def load_labels(path: Path) -> dict[str, bool]:
    labels = {}
    with path.open(newline="") as source:
        reader = csv.DictReader(source)
        if not {"run_id", "gamed"}.issubset(reader.fieldnames or []):
            raise ValueError("labels require run_id and gamed columns")
        for row in reader:
            run_id = row["run_id"]
            if not run_id or row["gamed"] not in ("0", "1"):
                raise ValueError(f"invalid label for {run_id!r}: expected 0 or 1")
            if run_id in labels:
                raise ValueError(f"duplicate label: {run_id}")
            labels[run_id] = row["gamed"] == "1"
    return labels


def classify_runs(rows: list[dict], labels: dict[str, bool]) -> dict[str, bool | None]:
    result = {}
    for row in rows:
        run_id = row["run_id"]
        if run_id in result:
            raise ValueError(f"duplicate run: {run_id}")
        if row["condition"] == "conflict":
            value = row.get("gamed_by_construction")
            if value not in ("True", "False"):
                raise ValueError(f"invalid conflict classification: {run_id}")
            if run_id in labels:
                raise ValueError(f"conflict run must use construction rule: {run_id}")
            result[run_id] = value == "True"
        else:
            result[run_id] = labels.get(run_id)
    unknown = labels.keys() - result.keys()
    if unknown:
        raise ValueError(f"labels contain unknown run IDs: {', '.join(sorted(unknown))}")
    return result


def require_complete(classifications: dict[str, bool | None]) -> None:
    missing = [run_id for run_id, label in classifications.items() if label is None]
    if missing:
        raise ValueError(f"{len(missing)} runs unclassified: {', '.join(missing)}")
