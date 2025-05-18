#!/usr/bin/env python3
"""
finpension_to_parqet.py

Converts Finpension transaction CSV exports to Parqet-compatible CSVs.

- Maps Finpension categories to Parqet types (Buy, Sell, Dividend, TransferIn/Out).
- Outputs CSV with semicolon separator, comma decimal mark, 5 decimal places.
- Usage: python finpension_to_parqet.py input.csv output.csv

Requires: pandas
"""

import sys
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


def convert(in_csv: str, out_csv: str) -> None:
    """
    Reads transactions from `in_csv`, transforms each row, and writes the result to `out_csv` in Parqet format.
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

        rows.append(
            {
                "date":   r["Date"],                      # yyyy-MM-dd
                "price":  float(r.get("Asset Price in CHF") or 0),
                "shares": float(r.get("Number of Shares") or 0),
                "tax":    0.0,
                "fee":    0.0,
                "type":   _map_type(r["Category"], float(r.get("Cash Flow") or 0)),
                "isin":   r.get("ISIN", ""),
            }
        )

    out_df = pd.DataFrame(rows, columns=[
        "date", "price", "shares", "tax", "fee", "type", "isin"
    ])
    _parqet_csv_write(out_df, out_csv)
    print(f"✔ {len(out_df)} activities written to {out_csv!r}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python finpension_to_parqet.py transaktions_report.csv parqet.csv")
    convert(sys.argv[1], sys.argv[2])
