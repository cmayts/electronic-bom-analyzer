"""Input readers and report writers."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def read_bom(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))
    if suffix == ".xlsx":
        try:
            from openpyxl import load_workbook
        except ImportError as exc:
            raise RuntimeError("XLSX support requires: pip install openpyxl") from exc
        workbook = load_workbook(path, read_only=True, data_only=True)
        sheet = workbook.active
        rows = sheet.iter_rows(values_only=True)
        headers = [str(value or "").strip() for value in next(rows, ())]
        return [dict(zip(headers, row, strict=False)) for row in rows]
    raise ValueError(f"Unsupported input format: {suffix or '<none>'}")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_normalized_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "part_number",
        "manufacturer",
        "manufacturer_part_number",
        "description",
        "quantity",
        "references",
        "source_rows",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
