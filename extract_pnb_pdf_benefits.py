#!/usr/bin/env python3
"""Extract the benefits content out of the PNB card benefit PDFs.

The PNB "Benefits Cured with Card" PDFs are a two-column table:
  left column (~x=77)  = benefit name
  right column (~x=233) = offer description
The shared RuPay NCMC brochure has no such table — for it we keep the
raw text only and flag `table: false`.

Writes data/cards/debit/pnb/pdf-extracted.json, keyed by pdf file path:
  { "<pdfFile>": { "title", "text", "table": bool, "rows": [{title, description}] } }

Usage:
  python extract_pnb_pdf_benefits.py            # extract all PDFs in pdf/
  python extract_pnb_pdf_benefits.py --file X  # just one pdf
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PDF_DIR = ROOT / "data" / "cards" / "debit" / "pnb" / "pdf"
OUT = ROOT / "data" / "cards" / "debit" / "pnb" / "pdf-extracted.json"

COL_SPLIT = 200.0          # lines starting left of this x are benefit names
HEADER_Y = 150.0           # address block / title area sits above this y
TEXT_CAP = 6000            # raw text cap stored per document


def _lines(doc):
    """Yield (x0, y0, text) for every text line in the PDF."""
    for page in doc:
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            for line in block.get("lines", []):
                x0, y0, x1, y1 = line["bbox"]
                text = " ".join(s["text"] for s in line.get("spans", [])).strip()
                if text:
                    yield x0, y0, text


def extract(pdf: Path) -> dict:
    import fitz
    doc = fitz.open(pdf)
    lines = list(_lines(doc))
    doc.close()

    title = ""
    rows: list[dict] = []
    cur: dict | None = None
    text_parts: list[str] = []

    # find the document title: the line right above the "Benefits" header
    header_idx = next((i for i, (_, _, t) in enumerate(lines)
                       if t.strip() == "Benefits"), -1)
    if header_idx > 0:
        title = lines[header_idx - 1][2]

    for x0, y0, t in lines:
        text_parts.append(t)
        if y0 < HEADER_Y:
            continue
        if t in ("Benefits", "Offer Description"):
            continue
        if re.fullmatch(r"Page \d+ of \d+", t):
            continue
        if x0 < COL_SPLIT:
            if cur and cur.get("description"):
                rows.append(cur)
            cur = {"title": t, "description": ""}
        elif cur is not None:
            cur["description"] = (cur["description"] + " " + t).strip()
    if cur and cur.get("description"):
        rows.append(cur)

    # strip "Benefits Cured with Card" header artifacts from rows
    rows = [r for r in rows if r["title"].strip() != "Benefits Cured with Card"]
    # a single "row" that is just the brochure title is not a table
    table = len(rows) > 1
    if not table:
        rows = []
    return {
        "title": title,
        "text": " ".join(text_parts)[:TEXT_CAP],
        "table": table,
        "rows": rows,
    }


def main(argv=None):
    only = None
    if argv and "--file" in argv:
        only = argv[argv.index("--file") + 1]
    out: dict[str, dict] = {}
    if OUT.exists():
        out = json.loads(OUT.read_text(encoding="utf-8"))
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        rel = str(pdf.relative_to(ROOT))
        if only and rel != only:
            continue
        if rel in out and not only:
            continue
        try:
            data = extract(pdf)
            out[rel] = data
            print(f"{rel}: table={data['table']} rows={len(data['rows'])} title={data['title'][:60]!r}")
        except Exception as e:
            print(f"FAIL {rel}: {e}")
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n{len(out)} documents -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
