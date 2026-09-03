"""Column normalization rules for common BOM exports."""

from __future__ import annotations

import re

CANONICAL_FIELDS = (
    "part_number",
    "manufacturer",
    "manufacturer_part_number",
    "description",
    "quantity",
    "references",
)

ALIASES = {
    "part_number": {"partnumber", "partno", "internalpartnumber", "item", "itemnumber"},
    "manufacturer": {"manufacturer", "mfr", "brand", "make"},
    "manufacturer_part_number": {
        "manufacturerpartnumber",
        "mfrpartnumber",
        "mfrpn",
        "mpn",
    },
    "description": {"description", "desc", "partdescription", "componentdescription"},
    "quantity": {"quantity", "qty", "count", "amount"},
    "references": {
        "references",
        "reference",
        "referencedesignators",
        "designators",
        "refdes",
    },
}


def normalize_header(value: object) -> str:
    """Convert a header into a compact comparison key."""
    return re.sub(r"[^a-z0-9]", "", str(value or "").strip().lower())


def resolve_columns(headers: list[str]) -> dict[str, str]:
    """Map canonical fields to matching input headers."""
    resolved: dict[str, str] = {}
    for header in headers:
        normalized = normalize_header(header)
        for canonical, aliases in ALIASES.items():
            if canonical not in resolved and normalized in aliases:
                resolved[canonical] = header
                break
    return resolved
