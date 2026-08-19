#!/usr/bin/env python3
"""
Generates one MI report PDF per student from a scaled-scores Excel file.

USAGE:
    python generate_reports.py --scores path/to/scores.xlsx --out output/

    --scores   Path to the Excel workbook (Name, Class, School, + one
               column per activity, matching config/skill_taxonomy.json)
    --out      Folder to write PDFs into (created if it doesn't exist)
    --only     Optional: generate just one student by exact name, useful
               for testing a single report before running the whole batch

EXAMPLE (test on one student first):
    python generate_reports.py --scores sample_data/sample_scores.xlsx \\
        --out output/ --only "Girija Joshi"
"""

import argparse
import re
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from data_loader import load_students  # noqa: E402
from build_report import build_context  # noqa: E402
from pdf_generator import render_pdf  # noqa: E402


def safe_filename(name: str, class_: str) -> str:
    base = f"{name}_{class_}".strip()
    base = re.sub(r"[^\w\-]+", "_", base)
    return f"{base}_MI_Report.pdf"


def main():
    parser = argparse.ArgumentParser(description="Generate MI assessment report PDFs.")
    parser.add_argument("--scores", required=True, help="Path to scaled-scores Excel file")
    parser.add_argument("--out", required=True, help="Output folder for generated PDFs")
    parser.add_argument("--only", default=None, help="Generate a single student by exact name (for testing)")
    args = parser.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reading scores from {args.scores} ...")
    students = load_students(args.scores)
    print(f"Found {len(students)} student(s).")

    if args.only:
        students = [s for s in students if s["name"].strip().lower() == args.only.strip().lower()]
        if not students:
            print(f"No student found matching name '{args.only}'. Check spelling against the Excel file.")
            sys.exit(1)

    succeeded, failed = 0, []
    for student in students:
        try:
            context = build_context(student)
            filename = safe_filename(student["name"], student["class"])
            output_path = out_dir / filename
            render_pdf(context, str(output_path))
            print(f"  ✓ {student['name']} -> {filename}")
            succeeded += 1
        except Exception as e:
            print(f"  ✗ {student['name']} FAILED: {e}")
            traceback.print_exc()
            failed.append(student["name"])

    print(f"\nDone. {succeeded} report(s) generated in {out_dir.resolve()}")
    if failed:
        print(f"{len(failed)} student(s) failed: {failed}")
        sys.exit(1)


if __name__ == "__main__":
    main()
