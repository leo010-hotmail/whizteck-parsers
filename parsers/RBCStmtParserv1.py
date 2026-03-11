"""Parser for RBC bank statements leveraging Document Intelligence tables."""

from pathlib import Path
import re

import pandas as pd

from .shared import get_document_client


__all__ = ["parse_rbc_bank_statement"]


_DATE_PATTERN = re.compile(r"^\d{1,2}\s+[A-Za-z]{3}$")


def _parse_pdf_date(value: str | None, year: int):
    if pd.isna(value):
        return pd.NA

    candidate = str(value).strip()

    if not _DATE_PATTERN.match(candidate):
        return pd.NA

    try:
        return pd.to_datetime(f"{candidate} {year}", format="%d %b %Y").strftime("%Y-%m-%d")
    except ValueError:
        return pd.NA


def parse_rbc_bank_statement(file_path: Path, statement_year: int) -> pd.DataFrame:
    """Return cleaned rows from an RBC bank statement PDF."""

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

    if "source_table" in final_df:
        final_df = final_df[final_df["source_table"] != 0]

    header_mask = (
        final_df[0].astype(str).str.contains("date", case=False, na=False) |
        final_df[1].astype(str).str.contains("description", case=False, na=False)
    )

    header_indexes = final_df[header_mask].index
    if len(header_indexes) > 1:
        final_df = final_df.drop(header_indexes[1:])

    final_df = final_df[~final_df[1].astype(str).str.contains(
        r"opening\s+balance|closing\s+balance",
        case=False,
        na=False,
        regex=True,
    )]

    parsed_dates = final_df[0].apply(lambda value: _parse_pdf_date(value, statement_year))

    is_header = final_df[0].astype(str).str.strip().str.lower() == "date"
    final_df.loc[~is_header, 0] = parsed_dates.ffill()
    final_df.loc[~is_header, 0] = pd.to_datetime(
        final_df.loc[~is_header, 0],
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    return final_df.reset_index(drop=True)
