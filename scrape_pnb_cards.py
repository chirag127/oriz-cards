#!/usr/bin/env python3
"""Scrape PNB card index (https://pnb.bank.in/card-index.html).

For every debit-card tab on the page:
  - extract the official card name (accordion card-link anchor)
  - resolve the card's benefits PDF:
      1. a direct `uploadfile/Cards/*.pdf` link if the tab has one
      2. the "To know more about the Benefits Cured with Card" downloadprocess fid
      3. the first non-generic downloadprocess fid
      4. the shared generic fid (last resort)
  - download the PDF into data/cards/debit/pnb/pdf/<slug>.pdf
  - keep the tab's readable spec text (features/benefits) in the manifest
Emits data/cards/debit/pnb/manifest.json with one entry per card.

Usage:
  python scrape_pnb_cards.py                 # re-fetch page, full scrape + download
  python scrape_pnb_cards.py --html PATH     # use a local copy of the page
  python scrape_pnb_cards.py --no-download   # parse only, no PDF fetch
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "cards" / "debit" / "pnb" / "raw" / "card-index.html"
PDF_DIR = ROOT / "data" / "cards" / "debit" / "pnb" / "pdf"
MANIFEST = ROOT / "data" / "cards" / "debit" / "pnb" / "manifest.json"
URL = "https://pnb.bank.in/card-index.html"
BASE = "https://pnb.bank.in/"

# Fid shared by many card tabs as a generic fallback link.
GENERIC_FID = "zabu0PmYQAMbbUPhnrcN9A=="

# Tabs that are navigation containers / sub-tabs, not cards.
SKIP_TABS = {"nav_personal_tab", "nav_corporate_tab", "nav_international_tab",
             "nav_capitalservices_tab", "ruplaycard_tab", "ruplaycard_tab1"}


class TabParser(HTMLParser):
    """Collect the readable text of each card tab, tracking nesting."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards: dict[str, dict] = {}
        self._stack: list[tuple[str, str | None]] = []  # (tag, tab_id|None)
        self._cur: dict | None = None
        self._in_heading = 0

    @staticmethod
    def _tab_id(attrs) -> str | None:
        d = dict(attrs)
        tid = d.get("id", "")
        if tid.endswith("_tab") and tid not in SKIP_TABS and \
                re.fullmatch(r"[A-Za-z0-9_]+_tab", tid):
            return tid
        return None

    def handle_starttag(self, tag, attrs):
        tid = self._tab_id(attrs) if tag == "div" else None
        if tid:
            self._cur = {"tab": tid, "text": [], "headings": []}
            self.cards[tid] = self._cur
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._cur:
            self._in_heading += 1
            self._cur["headings"].append("")
        self._stack.append((tag, tid))

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._in_heading:
            self._in_heading -= 1
        if tag == "div" and self._stack:
            _, tid = self._stack.pop()
            if tid:
                self._cur = None
                for _, outer in reversed(self._stack):
                    if outer:
                        self._cur = self.cards.get(outer)
                        break

    def handle_data(self, data):
        if not self._cur:
            return
        s = data.strip()
        if not s:
            return
        if self._in_heading and self._cur["headings"]:
            self._cur["headings"][-1] += " " + s
        self._cur["text"].append(s)


def human_name(tab: str) -> str:
    return tab.replace("_tab", "").replace("_", " ").strip()


def slugify(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s or "card"


def fetch_html() -> str:
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def strip_tags(html_frag: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html_frag)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def tab_regions(src: str):
    """Yield (tab_id, region_html) for each card tab in document order."""
    positions = [(m.start(), m.group(1))
                 for m in re.finditer(r'<div[^>]*id="([A-Za-z0-9_]+_tab)"', src)
                 if m.group(1) not in SKIP_TABS]
    seen: set[str] = set()
    for i, (start, tid) in enumerate(positions):
        if tid in seen:
            continue
        seen.add(tid)
        end = positions[i + 1][0] if i + 1 < len(positions) else len(src)
        yield tid, src[start:end]


def resolve_pdf_url(region: str) -> str | None:
    """Pick the best benefits-PDF URL for a card tab region."""
    direct = re.findall(r'href="(uploadfile/[^"]*\.pdf)"', region)
    if direct:
        path = html.unescape(direct[0]).replace(" ", "%20")
        return urllib.parse.urljoin(BASE, path)
    m = re.search(r'Benefits Cured with Card, please <a href="downloadprocess\.aspx\?fid=([^"&]+)"',
                  region)
    if m:
        fid = m.group(1)
    else:
        fids = re.findall(r'downloadprocess\.aspx\?fid=([^"&]+)', region)
        non_generic = [f for f in fids if f != GENERIC_FID]
        fid = (non_generic or fids or [None])[0]
    if not fid:
        return None
    return BASE + "downloadprocess.aspx?fid=" + urllib.parse.quote(fid)


def download(url: str, dest: Path) -> bool:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        blob = r.read()
        ctype = r.headers.get("Content-Type", "")
    if "pdf" not in ctype.lower() and not blob[:4] == b"%PDF":
        print(f"  SKIP {dest.name}: not a PDF ({ctype!r}, {len(blob)} bytes)")
        return False
    dest.write_bytes(blob)
    return True


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", default=None, help="local copy of card-index.html")
    ap.add_argument("--no-download", action="store_true")
    a = ap.parse_args(argv)

    if a.html:
        src = Path(a.html).read_text(encoding="utf-8", errors="replace")
    else:
        print(f"Fetching {URL} ...")
        src = fetch_html()
        RAW.parent.mkdir(parents=True, exist_ok=True)
        RAW.write_text(src, encoding="utf-8")
        print(f"Saved raw html -> {RAW.relative_to(ROOT)}")

    p = TabParser()
    p.feed(src)

    # Official display names come from the accordion card-link anchors:
    #   <a class="collapsed card-link" data-toggle="collapse" href="#X_tab">NAME</a>
    link_names: dict[str, str] = {}
    for m in re.finditer(
        r'<a[^>]*class="[^"]*card-link[^"]*"[^>]*href="#([A-Za-z0-9_]+_tab)"[^>]*>(.*?)</a>',
        src, re.S):
        link_names[m.group(1)] = strip_tags(m.group(2))

    cards = []
    for tid, region in tab_regions(src):
        rec = p.cards.get(tid, {})
        name = link_names.get(tid, human_name(tid))
        text = " ".join(rec.get("text", []))
        headings = [re.sub(r"\s+", " ", h).strip() for h in rec.get("headings", [])]
        headings = [h for h in headings if h]
        pdf_url = resolve_pdf_url(region)
        cards.append({
            "tab": tid,
            "name": name,
            "slug": slugify(name),
            "pdfUrl": pdf_url,
            "headings": headings,
            "text": text,
            "textLength": len(text),
        })
    cards.sort(key=lambda c: c["name"])

    PDF_DIR.mkdir(parents=True, exist_ok=True)
    # Shared doc linked from every card tab that has no benefit PDF of its own.
    shared_url = BASE + "downloadprocess.aspx?fid=" + urllib.parse.quote(GENERIC_FID)
    shared_dest = PDF_DIR / "rupay-contactless-benefits.pdf"
    if not a.no_download and not (shared_dest.exists() and shared_dest.stat().st_size > 0):
        if download(shared_url, shared_dest):
            print(f"got   [shared] RuPay Contactless Benefits ({shared_dest.stat().st_size} b)")
        else:
            shared_dest.unlink(missing_ok=True)

    if not a.no_download:
        for c in cards:
            if c.get("pdfFile"):
                continue
            if not c["pdfUrl"]:
                c["pdfFile"] = None
                print(f"NO-PDF {c['name']}")
                continue
            dest = PDF_DIR / f"{c['slug']}.pdf"
            if dest.exists() and dest.stat().st_size > 0:
                c["pdfFile"] = str(dest.relative_to(ROOT))
                print(f"have  {c['name']}")
                continue
            if download(c["pdfUrl"], dest):
                c["pdfFile"] = str(dest.relative_to(ROOT))
                print(f"got   {c['name']} ({dest.stat().st_size} b)")
            else:
                c["pdfFile"] = None
                dest.unlink(missing_ok=True)
        # Cards whose tab only links card images (no benefit PDF) get the shared doc.
        if shared_dest.exists():
            shared_rel = str(shared_dest.relative_to(ROOT))
            for c in cards:
                if not c.get("pdfFile"):
                    c["pdfFile"] = shared_rel
                    c["pdfNote"] = "No card-specific PDF on the page; linked shared RuPay Contactless benefits doc."

    MANIFEST.write_text(json.dumps(cards, indent=2, ensure_ascii=False), encoding="utf-8")
    n_pdf = sum(1 for c in cards if c.get("pdfFile"))
    print(f"\nManifest: {len(cards)} cards, {n_pdf} with PDF -> "
          f"{MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
