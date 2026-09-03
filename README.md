# Electronic BOM Analyzer

A privacy-safe command-line tool for validating electronic Bills of Materials (BOMs). It reads CSV or XLSX files, normalizes common column names, detects missing data and duplicate or conflicting entries, and generates machine-readable reports.

## Features

- CSV and XLSX input support
- Flexible aliases for common BOM column names
- Required-field and quantity validation
- Duplicate manufacturer-part-number detection
- Conflict detection for inconsistent manufacturer or description data
- Reference-designator duplicate detection
- Consolidated component quantities
- JSON issue report and normalized CSV output
- Standard-library test suite

## Installation

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

CSV analysis works without third-party packages.

## Usage

Analyze the included synthetic example:

```bash
python -m bom_analyzer examples/synthetic_bom.csv --output results
```

The command creates `normalized_bom.csv` and `bom_report.json`. Exit code `0` means no errors were found; exit code `1` means validation errors exist.

## Supported columns

The analyzer recognizes common aliases for part number, manufacturer, manufacturer part number, description, quantity, and reference designators. Column matching ignores case, spaces, hyphens, and underscores.

## Example output

```text
Rows read: 5
Unique components: 4
Errors: 1
Warnings: 2
Report: results/bom_report.json
Normalized BOM: results/normalized_bom.csv
```

The data under `examples/` is synthetic and contains no customer, supplier, pricing, or procurement information.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Scope and limitations

This project performs structural validation and consolidation. It does not access distributor systems, recommend real substitute components, verify lifecycle status, or make purchasing decisions. Engineering review of datasheets and application requirements remains necessary.

## License

Released under the MIT License.
