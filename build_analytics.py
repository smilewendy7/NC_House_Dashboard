#下游analytics
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
RANGE_RE = re.compile(r"\$?\s*([\d,]+(?:\.\d+)?)([mk]?)", re.IGNORECASE)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, object]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def append_jsonl(path: Path, obj: Dict[str, object]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def to_float(s: object) -> Optional[float]:
    if s is None:
        return None
    txt = str(s).strip()
    if txt == "":
        return None
    txt = txt.replace(",", "").replace("%", "").replace("$", "")
    try:
        x = float(txt)
    except ValueError:
        return None
    if math.isnan(x) or math.isinf(x):
        return None
    return x


def pct_change(curr: Optional[float], prev: Optional[float]) -> Optional[float]:
    if curr is None or prev is None or prev == 0:
        return None
    return (curr - prev) / prev * 100.0


def month_minus_one(month: str) -> Optional[str]:
    if not MONTH_RE.match(month):
        return None
    y, m = month.split("-")
    yy = int(y)
    mm = int(m) - 1
    if mm == 0:
        yy -= 1
        mm = 12
    return f"{yy:04d}-{mm:02d}"


def month_minus_year(month: str) -> Optional[str]:
    if not MONTH_RE.match(month):
        return None
    y, m = month.split("-")
    return f"{int(y) - 1:04d}-{int(m):02d}"


def _parse_price_token(raw_num: str, suffix: str) -> Optional[float]:
    try:
        base = float(raw_num.replace(",", ""))
    except ValueError:
        return None

    unit = (suffix or "").lower()
    if unit == "m":
        return base * 1_000_000
    if unit == "k":
        return base * 1_000
    return base


def parse_range_bounds(label: str) -> Tuple[Optional[float], Optional[float]]:
    txt = (label or "").strip().lower()
    nums: List[float] = []
    for raw_num, suffix in RANGE_RE.findall(txt):
        parsed = _parse_price_token(raw_num, suffix)
        if parsed is not None:
            nums.append(parsed)

    if "under" in txt or "below" in txt:
        return (0.0, nums[0]) if nums else (0.0, None)

    if "over" in txt or "and over" in txt or "and up" in txt or "+" in txt:
        return (nums[0], None) if nums else (None, None)

    if "-" in txt or "to" in txt:
        if len(nums) >= 2:
            return nums[0], nums[1]
        if len(nums) == 1:
            return nums[0], None

    if len(nums) == 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None


@dataclass
class DQIssue:
    severity: str
    table: str
    key: str
    field: str
    issue: str
    value: str
    logged_at: str


def add_issue(
    issues: List[DQIssue],
    severity: str,
    table: str,
    key: str,
    field: str,
    issue: str,
    value: object,
) -> None:
    issues.append(
        DQIssue(
            severity=severity,
            table=table,
            key=key,
            field=field,
            issue=issue,
            value="" if value is None else str(value),
            logged_at=now_str(),
        )
    )


def build_monthly_metrics(monthly_rows: List[Dict[str, str]], issues: List[DQIssue]) -> List[Dict[str, object]]:
    by_month: Dict[str, Dict[str, str]] = {}
    for row in monthly_rows:
        month = (row.get("report_month") or "").strip()
        if not MONTH_RE.match(month):
            add_issue(issues, "WARN", "monthly_summary", month or "<missing>", "report_month", "invalid_month_format", month)
            continue
        by_month[month] = row

    out: List[Dict[str, object]] = []
    for month in sorted(by_month.keys()):
        row = by_month[month]

        listings = to_float(row.get("listings_y0"))
        sales = to_float(row.get("sales_y0"))
        median_price = to_float(row.get("median_price_y0"))
        inventory = to_float(row.get("months_inventory_current"))

        # Prefer same-series YoY using previous year's y0 when available.
        # Fallback to row-level y1 parsed from PDF when previous-year row is absent.
        prev_year = month_minus_year(month)
        prev_year_row = by_month.get(prev_year) if prev_year else None

        if prev_year_row is not None:
            yoy_listings = pct_change(listings, to_float(prev_year_row.get("listings_y0")))
            yoy_sales = pct_change(sales, to_float(prev_year_row.get("sales_y0")))
            yoy_price = pct_change(median_price, to_float(prev_year_row.get("median_price_y0")))
            yoy_inventory = pct_change(inventory, to_float(prev_year_row.get("months_inventory_current")))
        else:
            yoy_listings = pct_change(listings, to_float(row.get("listings_y1")))
            yoy_sales = pct_change(sales, to_float(row.get("sales_y1")))
            yoy_price = pct_change(median_price, to_float(row.get("median_price_y1")))
            yoy_inventory = None

        prev_month = month_minus_one(month)
        if prev_month and prev_month in by_month:
            prev_month_row = by_month[prev_month]
            mom_listings = pct_change(listings, to_float(prev_month_row.get("listings_y0")))
            mom_sales = pct_change(sales, to_float(prev_month_row.get("sales_y0")))
            mom_price = pct_change(median_price, to_float(prev_month_row.get("median_price_y0")))
            mom_inventory = pct_change(inventory, to_float(prev_month_row.get("months_inventory_current")))
        else:
            mom_listings = mom_sales = mom_price = mom_inventory = None

        parse_status = (row.get("parse_status") or "").strip()
        normalized_parse_status = parse_status.upper()
        if parse_status and normalized_parse_status != "OK":
            severity = "ERROR" if normalized_parse_status == "ERROR" else "WARN"
            add_issue(
                issues,
                severity,
                "monthly_summary",
                month,
                "parse_status",
                "upstream_parse_not_ok",
                parse_status,
            )

        out.append(
            {
                "report_month": month,
                "listings": listings,
                "sales": sales,
                "median_price": median_price,
                "months_inventory": inventory,
                "yoy_listings_pct": yoy_listings,
                "yoy_sales_pct": yoy_sales,
                "yoy_price_pct": yoy_price,
                "yoy_inventory_pct": yoy_inventory,
                "mom_listings_pct": mom_listings,
                "mom_sales_pct": mom_sales,
                "mom_price_pct": mom_price,
                "mom_inventory_pct": mom_inventory,
                "source_pdf": row.get("source_pdf", ""),
                "parsed_at": row.get("parsed_at", ""),
                "parse_status": parse_status,
                "parse_notes": row.get("parse_notes", ""),
                "built_at": now_str(),
            }
        )

    return out


def build_price_ranges_enriched(price_rows: List[Dict[str, str]], issues: List[DQIssue]) -> List[Dict[str, object]]:
    grouped: Dict[str, List[Dict[str, str]]] = {}
    for row in price_rows:
        month = (row.get("report_month") or "").strip()
        if not MONTH_RE.match(month):
            add_issue(issues, "WARN", "price_ranges", month or "<missing>", "report_month", "invalid_month_format", month)
            continue
        grouped.setdefault(month, []).append(row)

    out: List[Dict[str, object]] = []
    for month in sorted(grouped.keys()):
        prepared: List[Dict[str, object]] = []
        for row in grouped[month]:
            label = (row.get("price_range") or "").strip()
            range_min, range_max = parse_range_bounds(label)

            if range_min is None and range_max is None:
                add_issue(issues, "WARN", "price_ranges", month, "price_range", "cannot_parse_range_bounds", label)

            prepared.append(
                {
                    "report_month": month,
                    "price_range": label,
                    "range_min": range_min,
                    "range_max": range_max,
                    "listings": to_float(row.get("listings")),
                    "sales_prev_12mo": to_float(row.get("sales_prev_12mo")),
                    "months_inventory": to_float(row.get("months_inventory")),
                    "source_pdf": row.get("source_pdf", ""),
                    "parsed_at": row.get("parsed_at", ""),
                }
            )

        def rank_key(item: Dict[str, object]) -> Tuple[float, float]:
            min_v = float(item["range_min"]) if isinstance(item.get("range_min"), (int, float)) else float("inf")
            max_v = float(item["range_max"]) if isinstance(item.get("range_max"), (int, float)) else float("inf")
            return min_v, max_v

        prepared.sort(key=rank_key)
        for i, item in enumerate(prepared, 1):
            item["range_rank"] = i
            item["built_at"] = now_str()
            out.append(item)

    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Build analytics outputs from parsed CSVs.")
    ap.add_argument("--parsed-dir", default="data/parsed", help="Input parsed folder (default: data/parsed)")
    ap.add_argument("--out-dir", default="data/analytics", help="Output analytics folder (default: data/analytics)")
    ap.add_argument("--strict-dq", action="store_true", help="Exit 1 if any DQ ERROR exists")
    args = ap.parse_args()

    parsed_dir = Path(args.parsed_dir)
    out_dir = Path(args.out_dir)
    ensure_dir(out_dir)

    monthly_in = parsed_dir / "monthly_summary.csv"
    price_in = parsed_dir / "price_ranges.csv"

    if not monthly_in.exists() or not price_in.exists():
        print(f"[ERROR] Missing input(s): {monthly_in} / {price_in}", file=sys.stderr)
        sys.exit(2)

    issues: List[DQIssue] = []
    monthly_rows = read_csv(monthly_in)
    price_rows = read_csv(price_in)

    if not monthly_rows:
        add_issue(issues, "ERROR", "monthly_summary", "<all>", "<table>", "empty_input", "")
    if not price_rows:
        add_issue(issues, "ERROR", "price_ranges", "<all>", "<table>", "empty_input", "")

    monthly_metrics = build_monthly_metrics(monthly_rows, issues)
    price_enriched = build_price_ranges_enriched(price_rows, issues)

    monthly_out = out_dir / "monthly_metrics.csv"
    price_out = out_dir / "price_ranges_enriched.csv"
    dq_out = out_dir / "analytics_dq_issues.csv"
    run_log = out_dir / "build_analytics_run_log.jsonl"

    write_csv(
        monthly_out,
        [
            "report_month",
            "listings",
            "sales",
            "median_price",
            "months_inventory",
            "yoy_listings_pct",
            "yoy_sales_pct",
            "yoy_price_pct",
            "yoy_inventory_pct",
            "mom_listings_pct",
            "mom_sales_pct",
            "mom_price_pct",
            "mom_inventory_pct",
            "source_pdf",
            "parsed_at",
            "parse_status",
            "parse_notes",
            "built_at",
        ],
        monthly_metrics,
    )

    write_csv(
        price_out,
        [
            "report_month",
            "price_range",
            "range_min",
            "range_max",
            "range_rank",
            "listings",
            "sales_prev_12mo",
            "months_inventory",
            "source_pdf",
            "parsed_at",
            "built_at",
        ],
        price_enriched,
    )

    write_csv(
        dq_out,
        ["severity", "table", "key", "field", "issue", "value", "logged_at"],
        [issue.__dict__ for issue in issues],
    )

    summary = {
        "ts": now_str(),
        "inputs": {"monthly_summary": str(monthly_in), "price_ranges": str(price_in)},
        "outputs": {
            "monthly_metrics": str(monthly_out),
            "price_ranges_enriched": str(price_out),
            "dq_issues": str(dq_out),
        },
        "counts": {
            "monthly_in_rows": len(monthly_rows),
            "price_in_rows": len(price_rows),
            "monthly_metrics_rows": len(monthly_metrics),
            "price_enriched_rows": len(price_enriched),
            "dq_issues_rows": len(issues),
            "dq_error_rows": sum(1 for issue in issues if issue.severity == "ERROR"),
        },
        "args": {"parsed_dir": args.parsed_dir, "out_dir": args.out_dir, "strict_dq": args.strict_dq},
    }
    append_jsonl(run_log, summary)

    print(f"[OK] Wrote: {monthly_out}")
    print(f"[OK] Wrote: {price_out}")
    print(f"[OK] Wrote: {dq_out} (rows={len(issues)})")
    print(f"[OK] Wrote: {run_log}")

    has_dq_error = any(issue.severity == "ERROR" for issue in issues)
    if args.strict_dq and has_dq_error:
        print("[ERROR] strict-dq enabled and DQ ERROR rows found.", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

