from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Silence pdfminer noise like FontBBox warnings (logger-based)
logging.getLogger("pdfminer").setLevel(logging.ERROR)

# Import your single-file parser
# It must expose: parse_one_pdf, MONTHLY_FIELDS, PRICE_RANGE_FIELDS
import parse_one_pdf as p1


# ----------------------------
# Config / Data Structures
# ----------------------------

@dataclass(frozen=True)
class Job:
    pdf_path: str
    report_month: str


@dataclass
class JobResult:
    report_month: str
    pdf_path: str
    ok: bool
    a_row: Optional[Dict[str, Any]] = None
    b_rows: Optional[List[Dict[str, Any]]] = None
    error_type: Optional[str] = None
    error_msg: Optional[str] = None


# ----------------------------
# Utilities
# ----------------------------

MONTH_RE = re.compile(r"(\d{4}-\d{2})")


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def guess_month_from_filename(path: Path) -> Optional[str]:
    m = MONTH_RE.search(path.name)
    return m.group(1) if m else None


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    ensure_dir(path.parent)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    ensure_dir(path.parent)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# ----------------------------
# Worker (runs in subprocess)
# ----------------------------

def _run_one(job: Job) -> JobResult:
    """
    This runs in a separate process if --workers > 1.
    IMPORTANT: Do not write CSV files here. Return parsed data to the main process.
    """
    pdf_path = Path(job.pdf_path)
    try:
        a_row, b_rows = p1.parse_one_pdf(pdf_path, job.report_month)
        # parse_one_pdf() already sets parsed_at inside row(s).
        return JobResult(
            report_month=job.report_month,
            pdf_path=str(pdf_path),
            ok=True,
            a_row=a_row,
            b_rows=b_rows,
        )
    except Exception as e:
        return JobResult(
            report_month=job.report_month,
            pdf_path=str(pdf_path),
            ok=False,
            error_type=type(e).__name__,
            error_msg=str(e),
        )


# ----------------------------
# Main pipeline
# ----------------------------

def build_jobs(pdf_dir: Path, pattern: str, limit: Optional[int] = None) -> List[Job]:
    """
    Scan pdf_dir for PDFs and build jobs with report_month.
    """
    pdf_paths = sorted(pdf_dir.glob(pattern))
    jobs: List[Job] = []

    for p in pdf_paths:
        if p.suffix.lower() != ".pdf":
            continue
        rm = guess_month_from_filename(p)
        if not rm:
            # skip files without YYYY-MM in name; keep pipeline deterministic
            continue
        jobs.append(Job(pdf_path=str(p), report_month=rm))

    if limit is not None:
        jobs = jobs[:limit]

    return jobs


def load_existing_monthly(monthly_csv: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load existing monthly_summary.csv into a dict keyed by report_month.
    """
    out: Dict[str, Dict[str, Any]] = {}
    for r in read_csv_rows(monthly_csv):
        rm = r.get("report_month")
        if rm:
            out[rm] = r
    return out


def load_existing_price_ranges(price_csv: Path) -> List[Dict[str, Any]]:
    return read_csv_rows(price_csv)


def merge_price_ranges(existing: List[Dict[str, Any]], new_rows: List[Dict[str, Any]], month: str) -> List[Dict[str, Any]]:
    """
    Remove old rows for a month, append new, and return.
    """
    kept = [r for r in existing if r.get("report_month") != month]
    return kept + new_rows


def should_skip(month: str, existing_monthly: Dict[str, Dict[str, Any]], force: bool) -> bool:
    if force:
        return False
    return month in existing_monthly


def run_pipeline(
    pdf_dir: Path,
    out_dir: Path,
    pattern: str,
    workers: int,
    force: bool,
    limit: Optional[int],
    dry_run: bool,
) -> int:
    """
    Returns exit code: 0 ok, 1 if any failures.
    """
    ensure_dir(out_dir)

    monthly_csv = out_dir / "monthly_summary.csv"
    price_csv = out_dir / "price_ranges.csv"
    failures_csv = out_dir / "parse_failures.csv"
    run_log_jsonl = out_dir / "parse_run_log.jsonl"

    existing_monthly = load_existing_monthly(monthly_csv)
    existing_price_ranges = load_existing_price_ranges(price_csv)

    jobs_all = build_jobs(pdf_dir, pattern=pattern, limit=limit)

    # Apply skip logic
    jobs: List[Job] = []
    skipped: List[Job] = []
    for j in jobs_all:
        if should_skip(j.report_month, existing_monthly, force):
            skipped.append(j)
        else:
            jobs.append(j)

    print(f"[INFO] PDFs found: {len(jobs_all)} | to-parse: {len(jobs)} | skipped: {len(skipped)}")
    if not jobs:
        print("[INFO] Nothing to parse.")
        return 0

    if dry_run:
        print("[DRY RUN] Jobs to parse:")
        for j in jobs[:20]:
            print(f"  - {j.report_month}  {j.pdf_path}")
        if len(jobs) > 20:
            print(f"  ... and {len(jobs)-20} more")
        return 0

    # Run parsing (parallel or sequential)
    results: List[JobResult] = []
    t0 = datetime.now()

    if workers <= 1:
        for idx, j in enumerate(jobs, 1):
            r = _run_one(j)
            results.append(r)
            print(f"[{idx}/{len(jobs)}] {j.report_month} -> {'OK' if r.ok else 'FAIL'}")
    else:
        # Windows-safe multiprocessing: only parse in workers, write in main process
        with ProcessPoolExecutor(max_workers=workers) as ex:
            fut_map = {ex.submit(_run_one, j): j for j in jobs}
            done = 0
            for fut in as_completed(fut_map):
                j = fut_map[fut]
                r = fut.result()
                results.append(r)
                done += 1
                print(f"[{done}/{len(jobs)}] {j.report_month} -> {'OK' if r.ok else 'FAIL'}")

    dt = (datetime.now() - t0).total_seconds()
    print(f"[INFO] Parsing finished in {dt:.2f}s")

    # Sort results by report_month for deterministic outputs
    results.sort(key=lambda x: x.report_month)

    # Merge into in-memory tables
    failures: List[Dict[str, Any]] = []
    any_fail = False

    # We'll build new price ranges list incrementally
    merged_price = existing_price_ranges[:]

    for r in results:
        log_obj = {
            "ts": now_str(),
            "report_month": r.report_month,
            "pdf": r.pdf_path,
            "ok": r.ok,
        }

        if not r.ok:
            any_fail = True
            log_obj["error_type"] = r.error_type
            log_obj["error_msg"] = r.error_msg

            failures.append({
                "report_month": r.report_month,
                "pdf": r.pdf_path,
                "failure_type": "exception",
                "error_type": r.error_type,
                "error_msg": r.error_msg,
                "parse_status": "",
                "parse_notes": "",
                "logged_at": now_str(),
            })
            append_jsonl(run_log_jsonl, log_obj)
            continue

        assert r.a_row is not None and r.b_rows is not None

        # DQ gate: if parse_status exists and is FAIL, count as failure but still write row (optional)
        parse_status = str(r.a_row.get("parse_status", "OK"))
        parse_notes = str(r.a_row.get("parse_notes", ""))

        # Update monthly row
        existing_monthly[r.report_month] = r.a_row

        # Replace price ranges for that month
        merged_price = merge_price_ranges(merged_price, r.b_rows, r.report_month)

        log_obj["parse_status"] = parse_status
        log_obj["price_ranges_rows"] = len(r.b_rows)
        if parse_notes:
            log_obj["parse_notes"] = parse_notes

        # Record FAIL/WARN in failures sheet (without stopping pipeline)
        if parse_status.upper() != "OK":
            any_fail = True
            failures.append({
                "report_month": r.report_month,
                "pdf": r.pdf_path,
                "failure_type": "parse_status",
                "error_type": "",
                "error_msg": "",
                "parse_status": parse_status,
                "parse_notes": parse_notes,
                "logged_at": now_str(),
            })

        append_jsonl(run_log_jsonl, log_obj)

    # Write outputs once (atomic-ish behavior)
    monthly_out_rows = [existing_monthly[k] for k in sorted(existing_monthly.keys())]
    merged_price.sort(key=lambda x: (x.get("report_month", ""), x.get("price_range", "")))

    # Use fieldnames from parse_one_pdf module (single source of truth)
    write_csv_rows(monthly_csv, p1.MONTHLY_FIELDS, monthly_out_rows)
    write_csv_rows(price_csv, p1.PRICE_RANGE_FIELDS, merged_price)

    # Failures
    fail_fields = ["report_month", "pdf", "failure_type", "error_type", "error_msg", "parse_status", "parse_notes", "logged_at"]
    write_csv_rows(failures_csv, fail_fields, failures)

    print(f"[OK] Wrote: {monthly_csv}")
    print(f"[OK] Wrote: {price_csv}")
    print(f"[OK] Wrote: {failures_csv} (rows={len(failures)})")
    print(f"[OK] Wrote: {run_log_jsonl}")

    return 1 if any_fail else 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Batch-parse NC housing PDFs into CSVs (engineering-grade).")
    ap.add_argument("--pdf-dir", default="data/pdfs", help="Folder containing PDFs (default: data/pdfs)")
    ap.add_argument("--out-dir", default="data/parsed", help="Output folder for CSVs/logs (default: data/parsed)")
    ap.add_argument("--pattern", default="*.pdf", help="Glob pattern inside pdf-dir (default: *.pdf)")
    ap.add_argument("--workers", type=int, default=1, help="Parallel workers (default: 1). On Windows, keep modest like 2-4.")
    ap.add_argument("--force", action="store_true", help="Re-parse even if report_month already exists in monthly_summary.csv")
    ap.add_argument("--limit", type=int, default=None, help="Only parse first N PDFs (for testing).")
    ap.add_argument("--dry-run", action="store_true", help="List planned jobs without parsing.")
    args = ap.parse_args()

    pdf_dir = Path(args.pdf_dir)
    out_dir = Path(args.out_dir)

    if not pdf_dir.exists():
        print(f"[ERROR] pdf-dir not found: {pdf_dir}", file=sys.stderr)
        sys.exit(2)

    code = run_pipeline(
        pdf_dir=pdf_dir,
        out_dir=out_dir,
        pattern=args.pattern,
        workers=max(1, args.workers),
        force=args.force,
        limit=args.limit,
        dry_run=args.dry_run,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()