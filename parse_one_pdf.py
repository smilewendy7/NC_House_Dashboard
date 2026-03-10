from __future__ import annotations

import re
import csv
import argparse
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional, Dict, List, Tuple

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

NY_TZ = ZoneInfo("America/New_York")

MONTHLY_FIELDS = [
    "report_month",
    "listings_y0", "listings_y1", "listings_y2", "listings_y3",
    "sales_y0", "sales_y1", "sales_y2", "sales_y3",
    "median_price_y0", "median_price_y1", "median_price_y2", "median_price_y3",
    "months_inventory_current",
    "yoy_listings_pct", "yoy_sales_pct", "yoy_price_pct", "yoy_inventory_pct",
    "source_pdf", "parsed_at",
    "parse_status", "parse_notes",
]

PRICE_RANGE_FIELDS = [
    "report_month",
    "price_range",
    "listings",
    "sales_prev_12mo",
    "months_inventory",
    "source_pdf",
    "parsed_at",
]


# ----------------------------
# 0) Helpers
# ----------------------------

def now_ny_str() -> str:
    return datetime.now(NY_TZ).strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def normalize_text(s: str) -> str:
    if not s:
        return ""
    # remove odd glyphs that appear in PDFs (icons)
    s = s.replace("\u00a0", " ")
    s = s.replace("\u2013", "-")
    s = s.replace("\u2014", "-")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def guess_report_month_from_filename(pdf_path: Path) -> Optional[str]:
    m = re.search(r"(\d{4}-\d{2})", pdf_path.name)
    return m.group(1) if m else None



_MONTH_NAME_TO_NUM = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def infer_report_month_from_text(text: str) -> Optional[str]:
    """
    Try to infer report month from title text like:
      - "North Carolina - Feb. 2025"
      - "North Carolina - February 2025"
    """
    if not text:
        return None

    m = re.search(
        r"(?:North\s+Carolina\s*[-:]\s*)?"
        r"(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\.?\s+(\d{4})",
        text,
        flags=re.IGNORECASE,
    )
    if not m:
        return None

    month_token = m.group(1).rstrip('.').lower()
    year = m.group(2)
    month_num = _MONTH_NAME_TO_NUM.get(month_token)
    if month_num is None:
        return None
    return f"{year}-{month_num:02d}"



def parse_number(raw: str) -> Optional[float]:
    """
    Supports:
      61,933 -> 61933
      $380,000 -> 380000
      $362K -> 362000
      5.16 -> 5.16
      -23.1% -> -23.1
    """
    if raw is None:
        return None
    s = raw.strip()
    if not s:
        return None
    if s.lower() in {"n/a", "na"} or s in {"-", "—"}:
        return None

    # percent
    if s.endswith("%"):
        s = s[:-1].strip()

    s = s.replace("$", "").replace(",", "").strip()

    mult = 1.0
    if s.endswith(("K", "k")):
        mult = 1000.0
        s = s[:-1].strip()
    elif s.endswith(("M", "m")):
        mult = 1_000_000.0
        s = s[:-1].strip()

    try:
        return float(s) * mult
    except ValueError:
        return None


def clean_price_range(s: str) -> str:
    """
    Clean weird chars, keep common tokens.
    This prevents CSV weirdness and keeps ranges consistent.
    """
    s = s.strip()
    # normalize multiple spaces
    s = re.sub(r"\s+", " ", s)
    # remove stray quotes
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")
    # remove non-printing chars
    s = "".join(ch for ch in s if ch.isprintable())
    return s


# ----------------------------
# 1) PDF text extraction
# ----------------------------

def extract_text_from_pdf(pdf_path: Path) -> str:
    if pdfplumber is None:
        raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages: List[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text() or "")
    return normalize_text("\n\n".join(pages))


# ----------------------------
# 2) Block cutters (the most important improvement)
# ----------------------------

def cut_dashboard_block(text: str) -> Optional[str]:
    """
    Dashboard block is from the header line containing
      LISTINGS ... SALES ... MEDIAN SALES PRICE ... INVENTORY
    up to BEFORE "PRICE RANGE".

    This prevents A parsing from accidentally reading B numbers.
    """
    start_m = re.search(r"\bLISTINGS\b.*\bSALES\b.*\bMEDIAN\s+SALES\s+PRICE\b.*\bINVENTORY\b", text, flags=re.IGNORECASE)
    if not start_m:
        return None
    start = start_m.start()

    end_m = re.search(r"\bPRICE\s+RANGE\b", text[start:], flags=re.IGNORECASE)
    end = start + end_m.start() if end_m else min(len(text), start + 2500)

    return text[start:end]


def cut_price_range_block(text: str) -> Optional[str]:
    """
    Price range block starts at "PRICE RANGE" and ends before
    "This report is compiled by" (or end).
    """
    start_m = re.search(r"\bPRICE\s+RANGE\b", text, flags=re.IGNORECASE)
    if not start_m:
        return None
    start = start_m.start()
    tail = text[start:]

    stop_m = re.search(r"This report is compiled by", tail, flags=re.IGNORECASE)
    stop = stop_m.start() if stop_m else min(len(tail), 8000)

    return tail[:stop]


# ----------------------------
# 3) A parsing (dashboard)
# ----------------------------

def parse_dashboard_y0(block: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    More robust y0 parsing.

    Prefer the 'State ... State ... State ... State ... months' line:
      State 42,363 State 8,410 State $306,705 State 3.4 months

    Fallback:
      61,933 8,133 $380,000 5.16
    """

    # 1) Preferred: explicit "State ... State ... State ... State"
    # Allow noise words/icons between tokens; require 'months' near end.
    pat_state = re.compile(
        r"State\s+(\d[\d,]{2,})\s+State\s+(\d[\d,]{2,})\s+State\s+(\$?\d[\d,]*\.?\d*)\s+State\s+(\d[\d,]*\.?\d*)\s*months",
        flags=re.IGNORECASE
    )
    m = pat_state.search(block)
    if m:
        return (
            parse_number(m.group(1)),
            parse_number(m.group(2)),
            parse_number(m.group(3)),
            parse_number(m.group(4)),
        )

    # 2) Fallback: loose pattern anywhere in block
    # Add a guard: money must be >= 50000 to avoid grabbing 48,999 as "price"
    pat_loose = re.compile(
        r"\b(\d[\d,]{2,})\s+(\d[\d,]{2,})\s+(\$?\d[\d,]*\.?\d*[KkMm]?)\s+(\d[\d,]*\.?\d*)\b",
        flags=re.IGNORECASE
    )

    for mm in pat_loose.finditer(block):
        a = parse_number(mm.group(1))
        b = parse_number(mm.group(2))
        c = parse_number(mm.group(3))
        d = parse_number(mm.group(4))

        # Guardrails:
        # - listings/sales should be reasonably large
        # - price should be >= 50000
        # - inventory is usually between 0.1 and 50
        if a is None or b is None or c is None or d is None:
            continue
        if a < 5000 or b < 500:
            continue
        if c < 50000:
            continue
        if not (0.1 <= d <= 50):
            continue

        return (a, b, c, d)

    return (None, None, None, None)

def parse_dashboard_history(block: str, report_month: str) -> Tuple[List[Optional[float]], List[Optional[float]], List[Optional[float]]]:
    """
    Support BOTH layouts:
    A) single line contains 9 values:
       55,218 47,619 49,461 10,569 10,632 11,617 $362K $350K $345K
    B) three separate lines (fallback)

    Return:
      listings_hist [y1,y2,y3]
      sales_hist    [y1,y2,y3]
      price_hist    [y1,y2,y3]
    """
    mm = int(report_month[5:7])
    lines = [normalize_text(x) for x in block.splitlines() if normalize_text(x)]

    header_pat = re.compile(rf"\b{mm:02d}/\d{{2}}\s+{mm:02d}/\d{{2}}\s+{mm:02d}/\d{{2}}\b")
    header_idx = None
    for i, line in enumerate(lines):
        if header_pat.search(line):
            header_idx = i
            break
    if header_idx is None:
        return ([None, None, None], [None, None, None], [None, None, None])

    # --------
    # Try layout A: 9 values in ONE line
    # --------
    # We accept prices as $362K or $350K or $345K etc.
    nine_pat = re.compile(
        r"\b(\d[\d,]{2,})\s+(\d[\d,]{2,})\s+(\d[\d,]{2,})\s+"
        r"(\d[\d,]{2,})\s+(\d[\d,]{2,})\s+(\d[\d,]{2,})\s+"
        r"(\$?\d[\d,]*\.?\d*[KkMm]?)\s+(\$?\d[\d,]*\.?\d*[KkMm]?)\s+(\$?\d[\d,]*\.?\d*[KkMm]?)\b"
    )

    for i in range(header_idx + 1, min(len(lines), header_idx + 20)):
        m = nine_pat.search(lines[i])
        if not m:
            continue

        listings = [parse_number(m.group(1)), parse_number(m.group(2)), parse_number(m.group(3))]
        sales    = [parse_number(m.group(4)), parse_number(m.group(5)), parse_number(m.group(6))]
        prices   = [parse_number(m.group(7)), parse_number(m.group(8)), parse_number(m.group(9))]

        if (
            all(v is not None and v >= 10000 for v in listings) and
            all(v is not None and v >= 1000 for v in sales) and
            all(v is not None and v >= 50000 for v in prices)
        ):
            return (listings, sales, prices)

    # --------
    # Fallback layout B: three separate lines
    # --------
    three_ints = re.compile(r"\b(\d[\d,]{2,})\s+(\d[\d,]{2,})\s+(\d[\d,]{2,})\b")
    three_money = re.compile(r"\b(\$?\d[\d,]*\.?\d*[KkMm]?)\s+(\$?\d[\d,]*\.?\d*[KkMm]?)\s+(\$?\d[\d,]*\.?\d*[KkMm]?)\b")

    listings_vals = None
    listings_line_idx = None
    for i in range(header_idx + 1, min(len(lines), header_idx + 20)):
        m = three_ints.search(lines[i])
        if not m:
            continue
        vals = [parse_number(m.group(1)), parse_number(m.group(2)), parse_number(m.group(3))]
        if all(v is not None and v >= 10000 for v in vals):
            listings_vals = vals
            listings_line_idx = i
            break

    if listings_vals is None or listings_line_idx is None:
        return ([None, None, None], [None, None, None], [None, None, None])

    sales_vals = None
    sales_line_idx = None
    for i in range(listings_line_idx + 1, min(len(lines), listings_line_idx + 15)):
        m = three_ints.search(lines[i])
        if not m:
            continue
        vals = [parse_number(m.group(1)), parse_number(m.group(2)), parse_number(m.group(3))]
        if all(v is not None and v >= 1000 for v in vals):
            sales_vals = vals
            sales_line_idx = i
            break

    price_vals = None
    if sales_line_idx is not None:
        for i in range(sales_line_idx + 1, min(len(lines), sales_line_idx + 15)):
            m = three_money.search(lines[i])
            if not m:
                continue
            vals = [parse_number(m.group(1)), parse_number(m.group(2)), parse_number(m.group(3))]
            if all(v is not None and v >= 50000 for v in vals):
                price_vals = vals
                break

    def _to3(v):
        if v is None:
            return [None, None, None]
        return [v[0], v[1], v[2]]

    return (_to3(listings_vals), _to3(sales_vals), _to3(price_vals))


def parse_dashboard_yoy(block: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    YOY ... 12.1% ... -23.1% ... 4.9% ... 11.3%
    """
    m = re.search(r"\bYOY\b", block, flags=re.IGNORECASE)
    if not m:
        return (None, None, None, None)
    tail = block[m.start(): m.start() + 350]
    pcts = re.findall(r"(-?\d+\.?\d*)\s*%", tail)
    if len(pcts) < 4:
        return (None, None, None, None)
    return (parse_number(pcts[0] + "%"), parse_number(pcts[1] + "%"), parse_number(pcts[2] + "%"), parse_number(pcts[3] + "%"))


def dq_check_monthly(row: Dict[str, object]) -> Tuple[str, str]:
    """
    Engineering-grade data quality checks.

    Returns:
      ("OK"|"WARN"|"FAIL", "notes...")

    Philosophy:
      - FAIL: very likely wrong parse (do not trust)
      - WARN: suspicious but might be valid (needs review)
    """
    problems_fail: List[str] = []
    problems_warn: List[str] = []

    def f(key: str) -> Optional[float]:
        v = row.get(key)
        if v is None or v == "":
            return None
        try:
            return float(v)
        except Exception:
            return None

    def is_missing(*keys: str) -> bool:
        return any(f(k) is None for k in keys)

    # ----------------------------
    # 0) Required fields presence
    # ----------------------------
    # y0 headline values are fundamental; missing means parsing probably failed.
    if is_missing("listings_y0", "sales_y0", "median_price_y0", "months_inventory_current"):
        problems_fail.append("missing y0 headline fields")

    # history fields are expected in this report type
    if is_missing("listings_y1", "listings_y2", "listings_y3"):
        problems_warn.append("missing listings history (y1..y3)")
    if is_missing("sales_y1", "sales_y2", "sales_y3"):
        problems_warn.append("missing sales history (y1..y3)")
    if is_missing("median_price_y1", "median_price_y2", "median_price_y3"):
        problems_warn.append("missing price history (y1..y3)")

    # YoY block can be partially missing in some PDFs while core metrics are still valid.
    # Only warn when 2+ YoY fields are missing to reduce noisy false positives.
    yoy_keys = ["yoy_listings_pct", "yoy_sales_pct", "yoy_price_pct", "yoy_inventory_pct"]
    yoy_missing = sum(1 for k in yoy_keys if f(k) is None)
    if yoy_missing >= 2:
        problems_warn.append(f"missing many YoY fields ({yoy_missing}/4)")
    # If headline missing, we can stop early (still continue to add more notes).
    ly0 = f("listings_y0")
    sy0 = f("sales_y0")
    py0 = f("median_price_y0")
    iy0 = f("months_inventory_current")

    # ----------------------------
    # 1) Basic plausibility ranges
    # ----------------------------
    # These are state-level metrics, so we can use broad guardrails.
    if ly0 is not None and ly0 < 5_000:
        problems_fail.append("listings_y0 too small")
    if sy0 is not None and sy0 < 500:
        problems_fail.append("sales_y0 too small")

    # Median price must be realistic; your earlier failure was 48,999 which is impossible here.
    if py0 is not None and py0 < 50_000:
        problems_fail.append("median_price_y0 too small")
    # Also catch absurdly huge numbers due to column drift
    if py0 is not None and py0 > 5_000_000:
        problems_fail.append("median_price_y0 too large")

    # Inventory months: typical 0~30; allow up to 60 before calling FAIL
    if iy0 is not None and iy0 <= 0:
        problems_fail.append("months_inventory_current <= 0")
    if iy0 is not None and iy0 > 60:
        problems_fail.append("months_inventory_current too large (>60)")

    # ----------------------------
    # 2) Cross-field relationships (detect misalignment)
    # ----------------------------
    # If parsing drifted, these relationships break in obvious ways.

    # A) sales should not exceed listings in the same month (almost always true for active+pending listings vs monthly sales)
    if ly0 is not None and sy0 is not None and sy0 > ly0:
        problems_warn.append("sales_y0 > listings_y0 (suspicious)")

    # B) Inventory months should not look like a big integer (e.g., 8877)
    if iy0 is not None and iy0 >= 500:
        problems_fail.append("months_inventory_current looks like a count (>=500), likely mis-parse")

    # ----------------------------
    # 3) History plausibility + drift detection
    # ----------------------------
    ly1, ly2, ly3 = f("listings_y1"), f("listings_y2"), f("listings_y3")
    sy1, sy2, sy3 = f("sales_y1"), f("sales_y2"), f("sales_y3")
    py1, py2, py3 = f("median_price_y1"), f("median_price_y2"), f("median_price_y3")

    # A) History values should be in reasonable ranges too
    for k in ["listings_y1", "listings_y2", "listings_y3"]:
        v = f(k)
        if v is not None and v < 5_000:
            problems_warn.append(f"{k} too small")
    for k in ["sales_y1", "sales_y2", "sales_y3"]:
        v = f(k)
        if v is not None and v < 500:
            problems_warn.append(f"{k} too small")
        if v is not None and v > 80_000:
            problems_fail.append(f"{k} too large (likely price-range contamination)")
    for k in ["median_price_y1", "median_price_y2", "median_price_y3"]:
        v = f(k)
        if v is not None and v < 50_000:
            problems_fail.append(f"{k} too small (likely drift)")
        if v is not None and v > 5_000_000:
            problems_fail.append(f"{k} too large (likely drift)")

    # B) Catch the exact failure mode you saw:
    #    y0 accidentally equals one of listings history numbers (very likely wrong)
    #    In your bad 2024-01 parse, y0 became 44,763 instead of 42,363.
    if ly0 is not None and any(v is not None and abs(ly0 - v) < 1e-6 for v in [ly1, ly2, ly3]):
        problems_warn.append("listings_y0 equals one of listings_y1..y3 (possible y0 drift)")

    # C) Strong drift signal: median_price_y0 equals one of listings history (impossible)
    if py0 is not None and any(v is not None and abs(py0 - v) < 1e-6 for v in [ly1, ly2, ly3, sy1, sy2, sy3]):
        problems_fail.append("median_price_y0 equals a count-like history value (definite drift)")

    # D) Strong drift signal: sales_y0 equals listings history (very unlikely)
    if sy0 is not None and any(v is not None and abs(sy0 - v) < 1e-6 for v in [ly1, ly2, ly3]):
        problems_fail.append("sales_y0 equals listings history (definite drift)")

    # E) YOY sanity range (percent)
    for k in ["yoy_listings_pct", "yoy_sales_pct", "yoy_price_pct", "yoy_inventory_pct"]:
        v = f(k)
        if v is None:
            continue
        # YoY outside [-100, 500] is almost surely wrong parse
        if v < -100 or v > 500:
            problems_warn.append(f"{k} out of expected range")

    # ----------------------------
    # 4) Decide status
    # ----------------------------
    if problems_fail:
        return ("FAIL", "; ".join(problems_fail + problems_warn))
    if problems_warn:
        return ("WARN", "; ".join(problems_warn))
    return ("OK", "")

def build_monthly_summary_row(text: str, report_month: str, source_pdf: str) -> Dict[str, object]:
    parsed_at = now_ny_str()
    block = cut_dashboard_block(text) or ""

    listings_y0, sales_y0, price_y0, inv_y0 = parse_dashboard_y0(block)
    listings_hist, sales_hist, price_hist = parse_dashboard_history(block, report_month)
    yoy_l, yoy_s, yoy_p, yoy_i = parse_dashboard_yoy(block)

    row = {
        "report_month": report_month,

        "listings_y0": listings_y0,
        "listings_y1": listings_hist[0], "listings_y2": listings_hist[1], "listings_y3": listings_hist[2],

        "sales_y0": sales_y0,
        "sales_y1": sales_hist[0], "sales_y2": sales_hist[1], "sales_y3": sales_hist[2],

        "median_price_y0": price_y0,
        "median_price_y1": price_hist[0], "median_price_y2": price_hist[1], "median_price_y3": price_hist[2],

        "months_inventory_current": inv_y0,

        "yoy_listings_pct": yoy_l,
        "yoy_sales_pct": yoy_s,
        "yoy_price_pct": yoy_p,
        "yoy_inventory_pct": yoy_i,

        "source_pdf": source_pdf,
        "parsed_at": parsed_at,
    }

    status, notes = dq_check_monthly(row)

    inferred_report_month = infer_report_month_from_text(text)
    if inferred_report_month and inferred_report_month != report_month:
        mismatch_note = (
            f"title month mismatch (expected {report_month}, found {inferred_report_month})"
        )
        notes = f"{notes}; {mismatch_note}" if notes else mismatch_note
        if status == "OK":
            status = "WARN"

    row["parse_status"] = status
    row["parse_notes"] = notes
    return row


# ----------------------------
# 4) B parsing (price ranges)
# ----------------------------

PRICE_RANGE_PAT = re.compile(
    r"""^(
        Below\s+\$?\d[\d,]* |
        Under\s+\$?\d[\d,]* |
        \$\d[\d,]*\s*-\s*\$\d[\d,]* |
        \$\d+(?:\.\d+)?[KkMm]\s*-\s*\$\d+(?:\.\d+)?[KkMm] |
        \$\d[\d,]*\+ |
        \$\d+(?:\.\d+)?[KkMm]\+ |
        \$\d+(?:\.\d+)?[KkMm]\s+and\s+up |
        \$\d[\d,]*\s+and\s+up
    )""",
    flags=re.IGNORECASE | re.VERBOSE
)


def parse_price_range_rows(block: str, report_month: str, source_pdf: str) -> List[Dict[str, object]]:
    parsed_at = now_ny_str()
    lines = [normalize_text(x) for x in block.splitlines() if normalize_text(x)]
    rows: List[Dict[str, object]] = []

    for line in lines:
        # skip noise
        if re.search(r"Listings Trends|increase|decrease|PRESENTED BY|Contact:", line, re.IGNORECASE):
            continue
        if re.search(r"PRICE\s+RANGE", line, re.IGNORECASE) and len(line.split()) <= 8:
            continue

        m = PRICE_RANGE_PAT.search(line)
        if not m:
            continue

        pr = clean_price_range(m.group(1))
        rest = line[m.end():].strip()

        nums = re.findall(r"(\d[\d,]*\.?\d*)", rest)
        if len(nums) < 3:
            continue

        rows.append({
            "report_month": report_month,
            "price_range": pr,
            "listings": parse_number(nums[0]),
            "sales_prev_12mo": parse_number(nums[1]),
            "months_inventory": parse_number(nums[2]),
            "source_pdf": source_pdf,
            "parsed_at": parsed_at,
        })

    return rows


# ----------------------------
# 5) CSV IO (A upsert, B replace month)
# ----------------------------

def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,  # auto-quote when needed (commas etc.)
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)


def upsert_monthly_summary(path: Path, new_row: Dict[str, object]) -> None:
    rows = read_csv_rows(path)
    by_month: Dict[str, Dict[str, object]] = {}
    for r in rows:
        rm = r.get("report_month")
        if rm:
            by_month[rm] = r
    by_month[new_row["report_month"]] = new_row
    out = [by_month[k] for k in sorted(by_month.keys())]
    write_csv_rows(path, MONTHLY_FIELDS, out)


def replace_price_ranges_for_month(path: Path, report_month: str, new_rows: List[Dict[str, object]]) -> None:
    rows = read_csv_rows(path)
    kept = [r for r in rows if r.get("report_month") != report_month]
    out = kept + new_rows
    out.sort(key=lambda r: (r.get("report_month", ""), r.get("price_range", "")))
    write_csv_rows(path, PRICE_RANGE_FIELDS, out)


# ----------------------------
# 6) Parse one PDF
# ----------------------------

def parse_one_pdf(pdf_path: Path, report_month: Optional[str]) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    report_month = report_month or guess_report_month_from_filename(pdf_path)
    if not report_month:
        raise ValueError("Need report_month. Provide --report-month YYYY-MM or include YYYY-MM in filename.")

    text = extract_text_from_pdf(pdf_path)

    # Save debug text (always)
    debug_txt = Path("data/parsed") / f"debug_text_{report_month}.txt"
    ensure_dir(debug_txt.parent)
    debug_txt.write_text(text, encoding="utf-8")

    a_row = build_monthly_summary_row(text, report_month, str(pdf_path))

    pr_block = cut_price_range_block(text)
    b_rows: List[Dict[str, object]] = []
    if pr_block:
        b_rows = parse_price_range_rows(pr_block, report_month, str(pdf_path))

    return a_row, b_rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--report-month", required=False)
    ap.add_argument("--out-dir", default="data/parsed")
    args = ap.parse_args()

    pdf_path = Path(args.pdf)
    out_dir = Path(args.out_dir)

    monthly_csv = out_dir / "monthly_summary.csv"
    price_csv = out_dir / "price_ranges.csv"

    a_row, b_rows = parse_one_pdf(pdf_path, args.report_month)

    upsert_monthly_summary(monthly_csv, a_row)
    replace_price_ranges_for_month(price_csv, a_row["report_month"], b_rows)

    print(f"[OK] Parsed PDF: {pdf_path}")
    print(f"[OK] A upserted: {monthly_csv} (status={a_row.get('parse_status')})")
    if a_row.get("parse_notes"):
        print(f"[WARN] A parse_notes: {a_row['parse_notes']}")
    print(f"[OK] B replaced-month: {price_csv}")
    print(f"[INFO] price_ranges rows written for {a_row['report_month']}: {len(b_rows)}")


if __name__ == "__main__":
    main()