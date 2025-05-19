#!/usr/bin/env python3
"""
finpension_to_parqet.py

Converts Finpension transaction CSV exports to Parqet-compatible CSVs.

- Maps Finpension categories to Parqet types (Buy, Sell, Dividend, TransferIn/Out).
- Outputs CSV with semicolon separator, comma decimal mark, 5 decimal places.
- Usage: python finpension_to_parqet.py input.csv output.csv

Requires: pandas
"""

import argparse

import pandas as pd


def _map_type(category: str, cash_flow) -> str:
    """
    Translate FinPension’s `Category` into Parqet’s `type` column.
    Transfers become TransferIn / TransferOut depending on cash-flow sign.
    """
    cat = str(category).strip()
    if cat in {"Buy", "Sell", "Dividend"}:
        return cat

    if cat == "Transfer":
        return "TransferIn" if (cash_flow or 0) >= 0 else "TransferOut"

    # fallback – keeps unsupported categories visible in Parqet
    return cat


def _parqet_csv_write(df: pd.DataFrame, path: str) -> None:
    """
    Write DataFrame in Parqet style:
    - semicolon separator
    - comma as decimal mark
    - 5 decimal places for floats
    """
    df.to_csv(
        path,
        sep=";",
        decimal=",",
        float_format="%.5f",
        index=False,
        encoding="utf-8-sig",
    )
    print(f"✔ {len(df)} activities written to {path!r}")


def create_transaction(date, category, price, amount, shares, isin, holding):
    """Creates a transaction dictionary with the specified details."""
    return {
        "date": date,  # yyyy-MM-dd
        "price": price,
        "amount": amount,
        "shares": shares,
        "tax": 0.0,
        "fee": 0.0,
        "type": category,
        "isin": isin,
        "currency": "CHF",
        "holding": holding,
    }


def _prepare_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure numeric columns are properly formatted as floats for consistent output.
    """
    numeric_columns = ["amount", "price", "shares", "tax", "fee"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return df


def convert(in_csv: str, out_csv: str, holding_account: str = "") -> None:
    """
    Reads transactions from `in_csv`, transforms each row, and writes the result to
    `out_csv` in Parqet format.
    Skips blank/summary lines, sets tax and fee to 0.0, and fills missing numeric fields with 0.
    Requires `_map_type` and `_parqet_csv_write` helpers.

        in_csv (str): Path to Finpension CSV input.
        out_csv (str): Path to Parqet CSV output.
    """
    transactions = pd.read_csv(in_csv, sep=";", decimal=".", dtype=str).replace({pd.NA: None})

    rows = []
    for _, r in transactions.iterrows():
        # Skip blank/summary lines
        if not r.get("Category"):
            continue

        cash_flow = float(r.get("Cash Flow") or 0)

        category = _map_type(r["Category"], cash_flow)

        if category in ("TransferIn", "TransferOut"):
            price = 1.0
            amount = cash_flow
            shares = cash_flow
            rows.append(
                create_transaction(
                    r["Date"],
                    category,
                    price,
                    amount,
                    shares,
                    "",
                    holding_account,
                )
            )
        else:
            if category == "Dividend":
                price = cash_flow
                amount = cash_flow
                shares = 1.0
                rows.append(
                    create_transaction(
                        r["Date"], "TransferIn", 1.0, cash_flow, cash_flow, "", holding_account
                    )
                )
            else:
                price = float(r.get("Asset Price in CHF"))
                amount = ""
                shares = float(r.get("Number of Shares"))
                cash_flow = abs(cash_flow)
                rows.append(
                    create_transaction(
                        r["Date"],
                        "TransferOut",
                        1.0,
                        cash_flow,
                        cash_flow,
                        "",
                        holding_account,
                    )
                )

            rows.append(
                create_transaction(
                    r["Date"],
                    category,
                    price,
                    amount,
                    shares,
                    r.get(
                        "ISIN",
                        "",
                    ),
                    "",
                )
            )

    out_df = pd.DataFrame(
        rows,
        columns=[
            "date",
            "amount",
            "price",
            "shares",
            "tax",
            "fee",
            "type",
            "isin",
            "currency",
            "holding",
        ],
    )
    out_df = _prepare_numeric_columns(out_df)  # Ensure numeric columns are properly formatted
    # Filter rows where type is "TransferIn" or "TransferOut"
    transaction_df = out_df[~out_df["type"].isin(["TransferIn", "TransferOut"])]

    _parqet_csv_write(transaction_df, out_csv)

    if holding_account:
        # Filter rows where holding is not empty
        transaction_df = out_df[out_df["holding"] != ""]
        _parqet_csv_write(transaction_df, out_csv.replace(".csv", "_cash_transactions.csv"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Finpension transaction CSV exports to Parqet-compatible CSVs."
    )
    parser.add_argument(
        "input_csv",
        help="Path to the Finpension CSV input file (e.g., transaktions_report.csv).",
    )
    parser.add_argument(
        "output_csv",
        help="Path to the Parqet CSV output file (e.g., parqet.csv).",
    )
    parser.add_argument(
        "--cash-account",
        type=str,
        required=False,
        help="Optional holding account ID of the cash account. If provided, it must have a value.",
    )

    args = parser.parse_args()

    if args.cash_account is not None and not args.cash_account.strip():
        parser.error("--cash-account was provided but no value was set.")

    args = parser.parse_args()

    convert(args.input_csv, args.output_csv, args.cash_account)
