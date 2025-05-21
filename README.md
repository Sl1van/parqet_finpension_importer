# parqet_finpension_importer

Convert a FinPension “transaktions_report.csv” into the Parqet-compatible csv.

## Usage
```bash
python finpension_to_parqet.py transaktions_report.csv parqet.csv [--cash-account CASH_ACCOUNT_ID]
```

* `transaktions_report.csv`: Path to the FinPension CSV export file.

* `parqet.csv`: Path for the Parqet-compatible CSV output.

* `--cash-account`: (optional) ID of the cash holding account. When provided, the script will generate an additional CSV file for cash transactions (see "Options" below).

## Options

**--cash-account**

If you provide the `--cash-account` option with an account ID, the script will:

* Write the main output file (e.g., `parqet.csv`) containing only non-cash transactions.
* Additionally, create a separate file (e.g., `parqet_cash_transactions.csv`) that contains only cash transactions, using the specified account ID as the holding account.
* If you do **not** provide this option, cash transactions will be ignored and not imported at all.

This allows you to track and import cash movements if your Parqet account has a dedicated cash account set up.

The cash account ID can be found with the help of this [blog article](https://www.parqet.com/blog/csv) (see section "Import von Cash Transaktionen").

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