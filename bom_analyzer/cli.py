"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import analyze
from .io import read_bom, write_json, write_normalized_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and normalize an electronic BOM.")
    parser.add_argument("input", type=Path, help="Input BOM in CSV or XLSX format")
    parser.add_argument("--output", type=Path, default=Path("results"), help="Output directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        rows = read_bom(args.input)
        report = analyze(rows)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Error: {exc}")
        return 2

    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "bom_report.json"
    normalized_path = args.output / "normalized_bom.csv"
    write_json(report_path, {key: value for key, value in report.items() if key != "normalized_rows"})
    write_normalized_csv(normalized_path, report["normalized_rows"])

    summary = report["summary"]
    print(f"Rows read: {summary['rows_read']}")
    print(f"Unique components: {summary['unique_components']}")
    print(f"Errors: {summary['errors']}")
    print(f"Warnings: {summary['warnings']}")
    print(f"Report: {report_path}")
    print(f"Normalized BOM: {normalized_path}")
    return 1 if summary["errors"] else 0
