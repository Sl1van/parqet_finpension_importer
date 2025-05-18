# parqet_finpension_importer

Convert a FinPension “transaktions_report.csv” into the Parqet-compatible csv.

## Usage
```bash
python finpension_to_parqet.py transaktions_report.csv parqet.csv
```

## Requirements
```bash
pip install pandas
```

## Development Setup

### Code style & pre-commit hook

This repository uses [**ruff**](https://github.com/astral-sh/ruff) for both
formatting and linting, wired into *pre-commit* so every commit stays clean.

```bash
pip install --upgrade ruff pre-commit   # one-time install
pre-commit install                      # set up the Git hook
```