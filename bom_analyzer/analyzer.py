"""BOM validation and consolidation logic."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from .schema import CANONICAL_FIELDS, resolve_columns


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    rows: list[int] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "rows": self.rows,
        }


def _clean(value: Any) -> str:
    return " ".join(str(value or "").strip().split())


def _parse_quantity(value: Any) -> int | None:
    text = _clean(value)
    if not re.fullmatch(r"\d+", text):
        return None
    number = int(text)
    return number if number > 0 else None


def _parse_references(value: Any) -> list[str]:
    return [token.strip().upper() for token in re.split(r"[,;\s]+", _clean(value)) if token.strip()]


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    headers = list(rows[0]) if rows else []
    columns = resolve_columns(headers)
    issues: list[Issue] = []

    for required in ("quantity", "manufacturer_part_number"):
        if required not in columns:
            issues.append(Issue("error", "missing_column", f"Required column not found: {required}"))

    normalized: list[dict[str, Any]] = []
    reference_rows: dict[str, list[int]] = defaultdict(list)

    for index, source in enumerate(rows, start=2):
        item = {field: _clean(source.get(columns.get(field, ""), "")) for field in CANONICAL_FIELDS}
        quantity = _parse_quantity(item["quantity"])
        if quantity is None:
            issues.append(Issue("error", "invalid_quantity", "Quantity must be a positive integer.", [index]))
            quantity = 0
        item["quantity"] = quantity
        item["source_rows"] = [index]

        if not item["manufacturer_part_number"]:
            issues.append(Issue("error", "missing_mpn", "Manufacturer part number is missing.", [index]))
        if not item["description"]:
            issues.append(Issue("warning", "missing_description", "Description is missing.", [index]))
        if not item["manufacturer"]:
            issues.append(Issue("warning", "missing_manufacturer", "Manufacturer is missing.", [index]))

        references = _parse_references(item["references"])
        item["references"] = references
        for reference in references:
            reference_rows[reference].append(index)
        normalized.append(item)

    for reference, source_rows in sorted(reference_rows.items()):
        if len(source_rows) > 1:
            issues.append(
                Issue("error", "duplicate_reference", f"Reference {reference} appears in multiple rows.", source_rows)
            )

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in normalized:
        key = item["manufacturer_part_number"].casefold()
        if key:
            groups[key].append(item)

    consolidated: list[dict[str, Any]] = []
    consumed: set[int] = set()
    for position, item in enumerate(normalized):
        if position in consumed or not item["manufacturer_part_number"]:
            if position not in consumed:
                consolidated.append(item)
            continue
        group = groups[item["manufacturer_part_number"].casefold()]
        positions = [idx for idx, candidate in enumerate(normalized) if candidate in group]
        consumed.update(positions)
        if len(group) > 1:
            issues.append(
                Issue(
                    "warning",
                    "duplicate_mpn",
                    f"Manufacturer part number {item['manufacturer_part_number']} occurs in multiple rows and was consolidated.",
                    [row for candidate in group for row in candidate["source_rows"]],
                )
            )
            for field_name in ("manufacturer", "description"):
                values = {candidate[field_name].casefold() for candidate in group if candidate[field_name]}
                if len(values) > 1:
                    issues.append(
                        Issue(
                            "error",
                            "conflicting_data",
                            f"Conflicting {field_name} values for {item['manufacturer_part_number']}.",
                            [row for candidate in group for row in candidate["source_rows"]],
                        )
                    )
        merged = dict(item)
        merged["quantity"] = sum(candidate["quantity"] for candidate in group)
        merged["references"] = sorted({ref for candidate in group for ref in candidate["references"]})
        merged["source_rows"] = [row for candidate in group for row in candidate["source_rows"]]
        consolidated.append(merged)

    serialized_rows = [
        {**item, "references": ", ".join(item["references"]), "source_rows": ", ".join(map(str, item["source_rows"]))}
        for item in consolidated
    ]
    error_count = sum(issue.severity == "error" for issue in issues)
    warning_count = sum(issue.severity == "warning" for issue in issues)
    return {
        "summary": {
            "rows_read": len(rows),
            "unique_components": len(consolidated),
            "total_quantity": sum(item["quantity"] for item in consolidated),
            "errors": error_count,
            "warnings": warning_count,
        },
        "columns": columns,
        "issues": [issue.as_dict() for issue in issues],
        "normalized_rows": serialized_rows,
    }
