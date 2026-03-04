from __future__ import annotations

import argparse
import csv
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def read_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv_rows(path: Path, fieldnames: Sequence[str], rows: List[Dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def merge_with_history(
    old_rows: List[Dict[str, str]],
    new_rows: List[Dict[str, str]],
    key_fields: Sequence[str],
) -> List[Dict[str, str]]:
    """
    Keep all historical rows so hidden website data does not disappear.
    Priority: new_rows overwrite same-key old_rows; old unique rows are preserved.
    """
    merged: List[Dict[str, str]] = []
    seen: set[Tuple[str, ...]] = set()

    def row_key(row: Dict[str, str]) -> Tuple[str, ...]:
        return tuple((row.get(k) or "").strip() for k in key_fields)

    for row in new_rows + old_rows:
        key = row_key(row)
        if key in seen:
            continue
        merged.append(row)
        seen.add(key)

    return merged


def preserve_csv_history(path: Path, key_fields: Sequence[str], log_file: Path) -> None:
    history_path = path.with_suffix(path.suffix + ".history")

    old_fields, old_rows = read_csv_rows(history_path)
    new_fields, new_rows = read_csv_rows(path)
    if not new_rows:
        return

    merged_rows = merge_with_history(old_rows=old_rows, new_rows=new_rows, key_fields=key_fields)
    merged_fields = list(dict.fromkeys([*new_fields, *old_fields]))

    write_csv_rows(path, merged_fields, merged_rows)
    write_csv_rows(history_path, merged_fields, merged_rows)

    msg = (
        f"[INFO] Preserved history for {path.name}: "
        f"new={len(new_rows)} old={len(old_rows)} merged={len(merged_rows)}"
    )
    print(msg)
    with log_file.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def build_steps(workers: int, force_extract: bool) -> List[List[str]]:
    extract_cmd = [sys.executable, "extract_pdfs.py", "--workers", str(workers)]
    if force_extract:
        extract_cmd.append("--force")

    return [
        [sys.executable, "fetch_index.py"],
        [sys.executable, "fetch_manifest.py"],
        [sys.executable, "download_pdfs.py"],
        extract_cmd,
    ]


def run_cmd(cmd: List[str], log_file: Path) -> int:
    pretty = " ".join(shlex.quote(c) for c in cmd)
    print(f"\n[RUN] {pretty}")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    assert proc.stdout is not None
    with log_file.open("a", encoding="utf-8") as f:
        f.write(f"\n[RUN] {pretty}\n")
        for line in proc.stdout:
            print(line, end="")
            f.write(line)

    return proc.wait()


def is_extract_step(cmd: Sequence[str]) -> bool:
    return len(cmd) > 1 and Path(cmd[1]).name == "extract_pdfs.py"


def failure_rows_count() -> int:
    failures_csv = Path("data") / "parsed" / "parse_failures.csv"
    _, rows = read_csv_rows(failures_csv)
    return len(rows)


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Run full NC housing ETL in one command: "
            "index -> manifest -> download -> extract"
        )
    )
    ap.add_argument("--workers", type=int, default=4, help="Workers for extract_pdfs.py (default: 4)")
    ap.add_argument("--force-extract", action="store_true", help="Pass --force to extract_pdfs.py")
    ap.add_argument("--dry-run", action="store_true", help="Print commands without executing")
    ap.add_argument(
        "--no-preserve-history",
        action="store_true",
        help="Disable merging current index/manifest/download outputs with local history",
    )
    ap.add_argument(
        "--strict-extract",
        action="store_true",
        help="Fail pipeline when extract_pdfs.py exits with 1 (parse warnings/failures).",
    )
    args = ap.parse_args()

    log_dir = Path("data") / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"pipeline_run_{now_ts()}.log"

    steps = build_steps(workers=max(1, args.workers), force_extract=args.force_extract)

    print(f"[INFO] Log file: {log_file}")
    print("[INFO] Steps:")
    for i, cmd in enumerate(steps, 1):
        print(f"  {i}. {' '.join(shlex.quote(c) for c in cmd)}")

    if args.no_preserve_history:
        print("[INFO] History preservation: OFF (snapshot-only mode)")
    else:
        print("[INFO] History preservation: ON (index/manifest/download outputs keep older rows)")

    if args.dry_run:
        print("[DRY RUN] No commands executed.")
        return

    history_targets = {
        "fetch_index.py": (Path("reports_index.csv"), ["report_month", "url"]),
        "fetch_manifest.py": (Path("reports_manifest.csv"), ["report_month", "pdf_url"]),
        "download_pdfs.py": (Path("reports_downloads.csv"), ["report_month", "pdf_url"]),
    }

    extract_warned = False
    for cmd in steps:
        code = run_cmd(cmd, log_file)
        if code != 0:
            if is_extract_step(cmd) and code == 1 and not args.strict_extract:
                extract_warned = True
                warn_msg = (
                    f"[WARN] extract_pdfs.py exited with 1 (usually parse_status warnings). "
                    f"parse_failures.csv rows={failure_rows_count()}. Continuing."
                )
                print("\n" + warn_msg)
                with log_file.open("a", encoding="utf-8") as f:
                    f.write("\n" + warn_msg + "\n")
            else:
                print(f"\n[ERROR] Step failed with exit code {code}: {' '.join(cmd)}")
                print(f"[ERROR] See log: {log_file}")
                sys.exit(code)

        if not args.no_preserve_history and len(cmd) > 1:
            script_name = Path(cmd[1]).name
            target = history_targets.get(script_name)
            if target:
                path, key_fields = target
                preserve_csv_history(path=path, key_fields=key_fields, log_file=log_file)

    if extract_warned:
        print("\n[OK] Full pipeline completed with extract warnings.")
    else:
        print("\n[OK] Full pipeline completed successfully.")
    print(f"[OK] Log saved to: {log_file}")


if __name__ == "__main__":
    main()


