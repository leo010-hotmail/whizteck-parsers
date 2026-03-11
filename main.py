"""FastAPI wrapper for the invoice and RBC parsers."""

from datetime import datetime
from io import BytesIO, StringIO
from pathlib import Path
import tempfile

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from parsers.InvoiceParser import parse_invoice_file
from parsers.RBCCCParser import parse_rbc_credit_card
from parsers.RBCStmtParserv1 import parse_rbc_bank_statement


app = FastAPI(title="Whizteck Parsing API")


def _serialize_dataframe_to_csv(df: pd.DataFrame, include_header: bool) -> bytes:
    buffer = StringIO()
    df.to_csv(buffer, index=False, header=include_header)
    buffer.seek(0)
    return buffer.getvalue().encode("utf-8")


async def _persist_upload(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "").suffix
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    try:
        contents = await upload.read()
        temp_file.write(contents)
    finally:
        temp_file.close()
        await upload.close()

    return Path(temp_file.name)


def _build_response(csv_bytes: bytes, filename: str) -> StreamingResponse:
    return StreamingResponse(
        BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _normalize_statement_year(value: int | None) -> int:
    candidate = value or datetime.utcnow().year
    if not 1900 <= candidate <= 2100:
        raise ValueError("Statement year must be between 1900 and 2100.")
    return candidate


@app.post("/parse/invoice", summary="Extract invoice metadata as CSV")
async def parse_invoice_endpoint(file: UploadFile = File(...)) -> StreamingResponse:
    path = await _persist_upload(file)

    try:
        df = parse_invoice_file(path)
    except Exception as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        path.unlink(missing_ok=True)

    csv_bytes = _serialize_dataframe_to_csv(df, include_header=True)
    return _build_response(csv_bytes, "invoice.csv")


@app.post(
    "/parse/rbc-credit-card",
    summary="Parse a credit-card statement and return CSV rows",
)
async def parse_rbc_credit_card_endpoint(
    file: UploadFile = File(...),
    statement_year: int | None = Form(None),
) -> StreamingResponse:
    year = _normalize_statement_year(statement_year)
    path = await _persist_upload(file)

    try:
        df = parse_rbc_credit_card(path, year)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    finally:
        path.unlink(missing_ok=True)

    csv_bytes = _serialize_dataframe_to_csv(df, include_header=False)
    return _build_response(csv_bytes, "credit-card.csv")


@app.post(
    "/parse/rbc-bank-statement",
    summary="Parse a bank statement and return cleaned CSV rows",
)
async def parse_rbc_bank_statement_endpoint(
    file: UploadFile = File(...),
    statement_year: int | None = Form(None),
) -> StreamingResponse:
    year = _normalize_statement_year(statement_year)
    path = await _persist_upload(file)

    try:
        df = parse_rbc_bank_statement(path, year)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    finally:
        path.unlink(missing_ok=True)

    csv_bytes = _serialize_dataframe_to_csv(df, include_header=False)
    return _build_response(csv_bytes, "bank-statement.csv")
