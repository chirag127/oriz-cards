#!/usr/bin/env python3
"""Build rich PNB debit-card JSONs from the scraped manifest.

Reads data/cards/debit/pnb/manifest.json (output of scrape_pnb_cards.py),
parses each card tab's spec text into schema fields (charges, limits,
benefits, insurance, lounge, features, validity, contactless/ncmc flags),
writes one <id>.json per card under data/cards/debit/pnb/, and upgrades the
matching entries in data/cards.json (the aggregate the site renders from).

Matching: ids/slugs are aligned with the aggregate by a normalized-name key
(prefix 'pnb' and suffix 'debit card' stripped), with manual overrides for
cards whose official name differs wildly. Existing rich per-card files
(e.g. pnb-ru-pay-select-neo-debit-card.json) are merged into, not replaced.

Usage:
  python build_pnb_cards.py            # write per-card JSONs + upgrade cards.json
  python build_pnb_cards.py --dry-run  # print plan only, write nothing
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PNB_DIR = ROOT / "data" / "cards" / "debit" / "pnb"
MANIFEST = PNB_DIR / "manifest.json"
AGGREGATE = ROOT / "data" / "cards.json"
PAGE_URL = "https://pnb.bank.in/card-index.html"
CUSTOMER_CARE = "1800 180 2222"

# Manual id overrides: scraped slug -> aggregate id (names too far apart to match).
ID_OVERRIDES = {
    "pnb-pay-banks-wearable-products-based-on-rupay-on-the-go-technology":
        "pnb-pay-wearable-rupay-debit",
    "rupay-pnb-palaash-debit-card-recycled-pvc-debit-card":
        "pnb-rupay-palaash-debit-card",
    "rupay-pnb-antah-drishti-braille-debit-card":
        "pnb-rupay-antah-drishthi-braille-debit-card",
    # aggregate carries a misspelt id ('vishawas'); merge into it to keep URLs stable
    "pnb-rupay-platinum-vishwas-varishth":
        "pnb-rupay-platinum-vishawas-varishth-debit-card",
}
NAME_OVERRIDES = {
    "pnb-pay-wearable-rupay-debit": "PNB Pay Wearable RuPay Debit Card",
    "pnb-rupay-palaash-debit-card": "PNB RuPay Palaash Debit Card",
    "pnb-rupay-antah-drishthi-braille-debit-card":
        "PNB RuPay Antah Drishthi Braille Debit Card",
}


# ─────────────────────────────────────────── helpers

def norm_key(s: str) -> str:
    n = re.sub(r"[^a-z0-9]+", "", s.lower())
    for suf in ("debitcard", "card"):
        if n.endswith(suf):
            n = n[: -len(suf)]
    if n.startswith("pnb"):
        n = n[3:]
    return n


def pretty_name(raw: str) -> str:
    s = (raw.replace("\u2019", "'").replace("\u2018", "'")
            .replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2013", "-").replace("\u2014", "-"))
    words = s.split()
    known = {"pnb": "PNB", "rupay": "RuPay", "mastercard": "MasterCard",
             "visa": "Visa", "ncmc": "NCMC", "ecom": "eCom", "pos": "POS",
             "atm": "ATM", "upi": "UPI", "amc": "AMC", "gst": "GST",
             "pvc": "PVC", "npci": "NPCI", "dmrc": "DMRC"}
    out = []
    for w in words:
        base = w.strip("()")
        low = base.lower()
        out.append(known.get(low, base.capitalize() if base else w))
    s = " ".join(out).replace("On The Go", "On-the-Go")
    s = s.rstrip(" )(")
    if not s.lower().endswith("card"):
        s += " Debit Card"
    return s


def first_amount(text: str) -> int | None:
    m = re.search(r"Rs\.?\s*([\d,]+(?:\.\d+)?)", text)
    if not m:
        return None
    try:
        return int(float(m.group(1).replace(",", "")))
    except ValueError:
        return None


def network_from(name: str) -> str:
    n = name.lower()
    if "mastercard" in n or "master card" in n:
        return "MasterCard"
    if "visa" in n:
        return "Visa"
    return "RuPay"


def tier_from(card_type: str, name: str) -> str:
    t = (card_type + " " + name).upper()
    for tier in ("PLATINUM", "GOLD", "SIGNATURE", "WORLD", "SELECT", "CLASSIC"):
        if tier in t:
            return tier.capitalize()
    return "Classic"


# ─────────────────────────────────────────── section splitter

MARKERS = [
    "Card Type", "Eligibility", "Usage", "ATM Limit (Cash Withdrawal) per day",
    "PoS / eCom Limits (Combined) per day", "Personal Accidental Insurance Cover*",
    "Lounge facility*", "Issuance Charges", "Annual Maintenance Charges (AMC)",
    "Replacement Charges", "Validity Period", "Other features / Benefits*",
    "Other features", "International Acceptance", "Contactless transactions",
    "Offline mode", "Exclusive Features for identification",
]
SPLIT_RE = re.compile(
    "(?=" + "|".join(re.escape(m) for m in MARKERS) + ")")


def split_sections(text: str) -> dict[str, str]:
    chunks = SPLIT_RE.split(text)
    out: dict[str, str] = {}
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        for m in MARKERS:
            if chunk.startswith(m):
                out.setdefault(m, chunk[len(m):].strip())
                break
    return out


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[a-z0-9%\)])\.\s+(?=[A-Z])", text)
    out = []
    for p in parts:
        p = p.strip().rstrip(".")
        if len(p) > 15 and p:
            out.append(p)
    return out


# ─────────────────────────────────────────── per-card parsing

def parse_card(c: dict) -> dict:
    sec = split_sections(c["text"])
    name = pretty_name(c["name"])
    card_type = sec.get("Card Type", "")
    usage_raw = sec.get("Usage", "")
    usage_l = usage_raw.lower()
    acc = sec.get("International Acceptance", "").strip()
    acc_l = acc.lower()
    if "global" in usage_l or "international" in usage_l:
        international = True
    elif "domestic" in usage_l:
        international = False
    elif acc:
        international = not acc_l.startswith(("not allowed", "not permitted"))
    else:
        international = False
    if acc_l.startswith(("not allowed", "not permitted")):
        international = False
    contactless = "contactless" in sec.get("Contactless transactions", "").lower()
    offline = sec.get("Offline mode", "").lower()
    ncmc = "works in offline (ncmc)" in offline or "ncmc" in offline or "ncmc" in card_type.lower()

    charges: list[dict] = []
    def add_charge(label: str, text: str):
        if not text or text.lower().startswith(("nil", "n/a", "not applicable")):
            charges.append({"label": label, "amount": 0, "note": "Nil"})
            return
        amt = first_amount(text)
        note = "Excluding GST" if "gst" in text.lower() else None
        if amt is None:
            entry = {"label": label, "note": text[:80]}
        else:
            entry = {"label": label, "amount": amt}
            if not note and "add-on" in text.lower():
                note = "Primary card; add-on card also charged"
            if note:
                entry["note"] = note
        charges.append(entry)

    add_charge("Issuance Fee", sec.get("Issuance Charges", ""))
    add_charge("Annual Fee", sec.get("Annual Maintenance Charges (AMC)", ""))
    add_charge("Replacement Fee", sec.get("Replacement Charges", ""))

    limits: dict[str, int] = {}
    atm = first_amount(sec.get("ATM Limit (Cash Withdrawal) per day", ""))
    if atm:
        limits["atmPerDay"] = atm
    pos = first_amount(sec.get("PoS / eCom Limits (Combined) per day", ""))
    if pos:
        limits["posEcomPerDay"] = pos
    if contactless:
        limits.setdefault("contactlessPerTxn", 5000)
        limits.setdefault("contactlessDailyLimit", 5000)

    benefits: list[dict] = []
    ins = sec.get("Personal Accidental Insurance Cover*", "")
    if ins and not any(x in ins.lower() for x in ("not available", "not applicable")):
        amt = first_amount(ins)
        b = {
            "category": "insurance",
            "title": "Personal Accidental Insurance Cover",
            "description": re.sub(r"\s+", " ", ins)[:300],
            "isSellable": False, "isActive": True, "activationRequired": True,
        }
        if amt:
            b["valueNum"] = amt
            b["valueStr"] = f"Rs. {amt:,}"
        benefits.append(b)
    lounge = sec.get("Lounge facility*", "")
    if lounge and "not applicable" not in lounge.lower() and "not available" not in lounge.lower():
        benefits.append({
            "category": "lounge",
            "title": "Airport Lounge Access",
            "description": re.sub(r"\s+", " ", lounge)[:300],
            "valueStr": "Complimentary" if "complimentary" in lounge.lower() else "Included",
            "isSellable": False, "isActive": True, "activationRequired": False,
        })

    features: list[str] = []
    for key in ("Other features / Benefits*", "Other features"):
        if key in sec:
            features.extend(split_sentences(sec[key]))
    if "Exclusive Features for identification" in sec:
        features.extend(split_sentences(sec["Exclusive Features for identification"]))
    features = list(dict.fromkeys(features))[:9]

    eligibility_notes = []
    elig = sec.get("Eligibility", "")
    if elig and "any pnb customer" not in elig.lower():
        eligibility_notes.append(re.sub(r"\s+", " ", elig)[:250])

    validity = "7 years" if sec.get("Validity Period", "").lower().startswith("7") else None

    usage = "International" if international else "Domestic"
    atm_s = f"Rs. {limits['atmPerDay']:,}/day" if limits.get("atmPerDay") else "bank-defined limits"
    pos_s = (f"PoS/eCom limit Rs. {limits['posEcomPerDay']:,}/day"
             if limits.get("posEcomPerDay") else "bank-defined PoS/eCom limits")
    if c["name"].lower() in name.lower():
        intro = f"{name} is a {c['name']} from Punjab National Bank."
    else:
        intro = f"{name} is a {network_from(name)} debit card from Punjab National Bank."
    desc = (f"{intro} {usage} usage; ATM limit {atm_s}, {pos_s}. "
            + ("Contactless payments supported. " if contactless else "")
            + ("NCMC offline transit enabled. " if ncmc else "")
            + f"Valid {validity or 'per bank policy'}.")
    return {
        "name": name,
        "cardType": "debit",
        "network": network_from(name),
        "tier": tier_from(card_type, name),
        "variant": card_type or None,
        "usage": usage,
        "internationalUsable": international,
        "contactless": contactless,
        "ncmc": ncmc,
        "validity": validity,
        "charges": charges,
        "limits": limits,
        "benefits": benefits,
        "features": features,
        "eligibility": {"existingAccountRequired": True, "notes": eligibility_notes}
                   if eligibility_notes else {"existingAccountRequired": True},
        "description": desc,
        "pdfFile": c.get("pdfFile"),
        "pdfUrl": c.get("pdfUrl"),
        "pdfNote": c.get("pdfNote"),
    }


# ─────────────────────────────────────────── merge + emit

def merge_card(base: dict, scraped: dict) -> dict:
    merged = dict(base)
    merged.update({k: v for k, v in scraped.items() if v is not None})
    merged.setdefault("bank", "Punjab National Bank")
    merged.setdefault("bankCode", "pnb")
    merged.setdefault("customerCareNumber", CUSTOMER_CARE)
    merged.setdefault("applyUrl", PAGE_URL)
    merged.setdefault("type", "debit")
    merged.setdefault("slug", merged["id"])
    dq = {
        "status": "auto-scraped",
        "sourceUrls": [PAGE_URL],
        "lastVerified": date.today().isoformat(),
    }
    existing_dq = merged.get("dataQuality") or {}
    existing_dq.update(dq)
    merged["dataQuality"] = existing_dq
    merged["lastUpdated"] = date.today().isoformat()
    return merged


def main(argv=None):
    dry = "--dry-run" in (argv or sys.argv[1:])
    cards = json.loads(MANIFEST.read_text(encoding="utf-8"))

    existing_files = {}
    for p in PNB_DIR.glob("*.json"):
        if p.name in ("manifest.json",):
            continue
        existing_files[json.loads(p.read_text(encoding="utf-8"))["id"]] = p

    aggregate = json.loads(AGGREGATE.read_text(encoding="utf-8"))
    agg_by_id = {c["id"]: c for c in aggregate}
    # index aggregate PNB debit entries by normalized name key
    key_to_agg = {}
    for c in aggregate:
        if c.get("bankCode") == "pnb" and c.get("cardType") == "debit":
            key_to_agg.setdefault(norm_key(c.get("name", "")), []).append(c)

    planned: list[tuple[str, dict]] = []
    new_ids: list[str] = []
    for c in cards:
        scraped = parse_card(c)
        oid = ID_OVERRIDES.get(c["slug"])
        key = norm_key(scraped["name"])
        if not oid:
            for cand in key_to_agg.get(key, []):
                oid = cand["id"]
                break
        if not oid:
            # prefix fallback: 'PNB RuPay Select NEO' vs
            # 'PNB RuPay Select NEO International Debit Card' -> same card
            for agg_key, cands in key_to_agg.items():
                if (agg_key.startswith(key) and
                        agg_key[len(key):] in {"international", "domestic", "debit"}):
                    oid = cands[0]["id"]
                    break
        if not oid:
            # fall back to slug-based id for brand-new cards
            oid = c["slug"] if c["slug"].endswith("-debit-card") else c["slug"] + "-debit-card"
        if oid not in agg_by_id:
            agg_by_id[oid] = None
            new_ids.append(oid)
        scraped["id"] = oid
        scraped["name"] = NAME_OVERRIDES.get(oid, scraped["name"])
        scraped["slug"] = oid
        scraped["tagline"] = (
            f"{scraped['network']} {scraped['tier']} debit card from PNB — "
            f"{scraped['usage'].lower()} usage with "
            f"{'NCMC transit' if scraped['ncmc'] else 'ATM + POS access'}.")
        base = agg_by_id.get(oid) or {}
        merged = merge_card(base, scraped)
        planned.append((oid, merged))

    if dry:
        for oid, _ in planned:
            print(f"PLAN {oid} (new)" if oid in new_ids else f"PLAN {oid}")
        print(f"\n{len(planned)} cards, {len(new_ids)} new ids")
        return

    # write per-card JSON files
    written = 0
    for oid, merged in planned:
        out = PNB_DIR / f"{oid}.json"
        out.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding="utf-8")
        written += 1
    print(f"Wrote {written} per-card JSONs -> {PNB_DIR}")

    # upgrade aggregate
    new_map = {oid: merged for oid, merged in planned}
    out_cards = []
    added = 0
    for c in aggregate:
        if c.get("bankCode") == "pnb" and c.get("cardType") == "debit" and c["id"] in new_map:
            out_cards.append(new_map[c["id"]])
        else:
            out_cards.append(c)
    present = {c["id"] for c in out_cards}
    for oid in new_ids:
        if oid not in present:
            out_cards.append(new_map[oid])
            added += 1
    AGGREGATE.write_text(json.dumps(out_cards, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Upgraded {len(new_map) - added} + appended {added} entries in {AGGREGATE.name}")


if __name__ == "__main__":
    main()
