"""Invoice parser that wraps the Document Intelligence workflow."""

from pathlib import Path

import pandas as pd

from .shared import get_document_client


def parse_invoice_file(file_path: Path) -> pd.DataFrame:
    """Return a single-row frame that holds the invoice metadata."""

    client = get_document_client()

    with open(file_path, "rb") as payload:
        poller = client.begin_analyze_document(
            model_id="prebuilt-invoice",
            body=payload,
        )

    result = poller.result()

    if not result.documents:
        raise ValueError("Document Intelligence did not return any documents.")

    invoice_fields = result.documents[0].fields

    return pd.DataFrame(
        [
            {
                "vendor": invoice_fields.get("VendorName", {}).get("content"),
                "invoice_date": invoice_fields.get("InvoiceDate", {}).get("content"),
                "total": invoice_fields.get("InvoiceTotal", {}).get("content"),
                "currency": invoice_fields.get("Currency", {}).get("content"),
            }
        ]
    )
