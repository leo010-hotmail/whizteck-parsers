"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

const PARSER_OPTIONS = [
  {
    label: "Invoice",
    value: "parse/invoice",
    helper: "Extracts vendor, date, total, and currency from invoices.",
  },
  {
    label: "Credit Card",
    value: "parse/rbc-credit-card",
    helper: "Normalizes credit card tables, including foreign currency details.",
  },
  {
    label: "Bank Statement",
    value: "parse/rbc-bank-statement",
    helper: "Cleans bank statement tables and normalizes transaction dates.",
  },
];

const gatewayUrl = process.env.NEXT_PUBLIC_API_GATEWAY_URL?.replace(/\/$/, "") ?? "";

export default function HomePage() {
  const [selectedParser, setSelectedParser] = useState(PARSER_OPTIONS[0].value);
  const [file, setFile] = useState<File | null>(null);
  const [statementYear, setStatementYear] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [downloadUrl, setDownloadUrl] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const parserInfo = useMemo(
    () => PARSER_OPTIONS.find((option) => option.value === selectedParser) ?? PARSER_OPTIONS[0],
    [selectedParser]
  );

  useEffect(() => {
    const current = downloadUrl;
    return () => {
      if (current) {
        URL.revokeObjectURL(current);
      }
    };
  }, [downloadUrl]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (!file) {
      setError("Please select a PDF file.");
      return;
    }

    if (!gatewayUrl) {
      setError("API gateway URL (NEXT_PUBLIC_API_GATEWAY_URL) is not configured.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    if (statementYear.trim()) {
      formData.append("statement_year", statementYear.trim());
    }

    try {
      setIsSubmitting(true);
      setStatus("Uploading file and waiting for the parser...");

      const response = await fetch(`/api/parse?parser=${selectedParser}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || response.statusText);
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setDownloadUrl(url);
      setStatus("Parsed CSV ready for download");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to parse the document.");
      setStatus("");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="parser-shell">
      <header>
        <p className="eyebrow">Document Parsing</p>
        <h1>Upload a PDF and get the parsed CSV</h1>
        <p className="subhead">
          The file is forwarded through the Azure API Management gateway to the FastAPI backend (Azure Container App), then
          to Azure Document Intelligence. Supply a statement year when parsing bank statements or credit-card files.
        </p>
      </header>

      <section className="card">
        <form onSubmit={handleSubmit} className="form-grid">
          <label className="input-group">
            <span>Parser</span>
            <select value={selectedParser} onChange={(event) => setSelectedParser(event.target.value)}>
              {PARSER_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            <small>{parserInfo.helper}</small>
          </label>

          <label className="input-group">
            <span>PDF file</span>
            <input
              type="file"
              accept=".pdf"
              onChange={(event) => setFile(event.target.files?.[0] ?? null)}
            />
          </label>

          <label className="input-group">
            <span>Statement year (optional)</span>
            <input
              type="number"
              min="1900"
              max="2100"
              placeholder="2025"
              value={statementYear}
              onChange={(event) => setStatementYear(event.target.value)}
              disabled={selectedParser === "parse/invoice"}
            />
            <small>Only required for bank or credit-card statements.</small>
          </label>

          <button type="submit" className="button" disabled={isSubmitting}>
            {isSubmitting ? "Processing..." : "Upload + Parse"}
          </button>
        </form>

        {status && <p className="status">{status}</p>}
        {error && <p className="error">{error}</p>}

        {downloadUrl && (
          <a
            className="button secondary"
            href={downloadUrl}
            download={`${parserInfo.label.replace(/\s+/g, "-")}.csv`}
          >
            Download {parserInfo.label} CSV
          </a>
        )}
      </section>

      <section className="card"> 
        <p className="subhead">API Gateway base URL</p>
        <p className="mono">{gatewayUrl || "Configure NEXT_PUBLIC_API_GATEWAY_URL in Vercel"}</p>
      </section>
    </div>
  );
}
