"""Credit card parser that normalizes RBC credit-card tables."""

from pathlib import Path
import re

import pandas as pd

from .shared import get_document_client


__all__ = ["parse_rbc_credit_card"]


_DATE_PATTERN = re.compile(r"^[A-Za-z]{3}\s+\d{1,2}$")


def _parse_pdf_date(value: str | None, year: int):
    if not value or str(value).strip() == "":
        return pd.NA

    candidate = str(value).strip()

    if not _DATE_PATTERN.match(candidate):
        return pd.NA

    try:
        return pd.to_datetime(f"{candidate} {year}", format="%b %d %Y").strftime("%Y-%m-%d")
    except ValueError:
        return pd.NA


def parse_rbc_credit_card(file_path: Path, statement_year: int) -> pd.DataFrame:
    """Return the table that Document Intelligence extracts from an RBC credit card PDF."""

    client = get_document_client()

    with open(file_path, "rb") as payload:
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout",
            body=payload,
        )

    result = poller.result()

    if not result.tables:
        return pd.DataFrame()

    all_tables: list[pd.DataFrame] = []

    for table_index, table in enumerate(result.tables):
        rows = table.row_count or 0
        cols = table.column_count or 0

        if rows == 0 or cols == 0:
            continue

        table_data = [["" for _ in range(cols)] for _ in range(rows)]

        for cell in table.cells:
            if cell.row_index < rows and cell.column_index < cols:
                table_data[cell.row_index][cell.column_index] = cell.content

        df = pd.DataFrame(table_data)
        df["source_table"] = table_index
        all_tables.append(df)

    if not all_tables:
        return pd.DataFrame()

    final_df = pd.concat(all_tables, ignore_index=True)

    col0_raw = final_df[0].astype(str).str.strip()
    is_header = col0_raw.str.contains(r"\btransaction\b", case=False, na=False)

    header_indexes = final_df[is_header].index
    first_header_index = header_indexes.min() if len(header_indexes) else None

    parsed_dates = col0_raw.apply(lambda val: _parse_pdf_date(val, statement_year))

    mask_keep = parsed_dates.notna() | (final_df.index == first_header_index)
    final_df = final_df[mask_keep].reset_index(drop=True)

    col0_raw = final_df[0].astype(str).str.strip()
    is_header = col0_raw.str.contains(r"\btransaction\b", case=False, na=False)
    parsed_dates = col0_raw.apply(lambda val: _parse_pdf_date(val, statement_year))

    final_df.loc[~is_header, 0] = parsed_dates[~is_header]

    if 6 not in final_df.columns:
        final_df[6] = pd.NA

    if 7 not in final_df.columns:
        final_df[7] = pd.NA

    if 2 not in final_df.columns:
        final_df[2] = ""

    desc = final_df[2].astype(str)

    fx_amount = desc.str.extract(
        r"Foreign\s+Currency-([A-Z]{3})\s+([\d,]+\.?\d{0,2})",
        expand=True,
    )

    fx_rate = desc.str.extract(r"Exchange\s+rate-([\d.]+)", expand=False)

    final_df.loc[fx_amount[0].notna(), 6] = fx_amount[0] + " " + fx_amount[1]
    final_df.loc[fx_rate.notna(), 7] = fx_rate

    return final_df
