# Jagrati MI Report Generator

Generates one polished, personalised Multiple Intelligence PDF report per
student from a spreadsheet of scaled scores (0-10). No AI/API calls, no
per-report cost — pure Python, runs entirely on your own machine.

## What it does

```
scores.xlsx (one row per student, scaled 0-10)
        ↓
scoring engine — groups sub-skills into intelligences, assigns each
intelligence a tier (Standout / Developing / Growth) based on an internal
average that is NEVER shown in the report, and picks the top 3
        ↓
narrative engine — fills in the "what this tells us" / "recommendations"
text using rule-based templates (config/, src/narrative.py)
        ↓
report_template.html (Jinja2) → rendered to PDF (WeasyPrint)
        ↓
output/StudentName_Class_MI_Report.pdf, one per student
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**WeasyPrint needs a couple of native libraries (Pango/Cairo) to render PDFs.**
This is the one non-trivial part of setup, and it's OS-specific:

- **Mac**: `brew install pango`
- **Ubuntu/Debian**: `sudo apt install libpango-1.0-0 libpangocairo-1.0-0`
- **Windows**: install the [GTK3 runtime](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)
  once, then `pip install weasyprint` as normal. WeasyPrint's own install
  docs (https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)
  have the current step-by-step if this changes.

Test the install worked:
```bash
python3 generate_reports.py --scores sample_data/sample_scores.xlsx --out output/ --only "Girija Joshi"
```
This should produce a 13-page PDF in `output/`. If it does, everything's working.

## Running it for real

```bash
python3 generate_reports.py --scores /path/to/your/grade_scores.xlsx --out /path/to/output_folder/
```

Drop the `--only "Student Name"` flag to run the whole file. Always test
with `--only` on one or two students first when you've changed a config
file, before running a full batch.

## Input file format (scores.xlsx)

One row per student. Required columns: `Name`, `Class`, `School`, plus
one column per activity — **column names must match `config/skill_taxonomy.json`
exactly** (case-insensitive, extra spaces ignored). Leave a cell blank if
that activity wasn't administered to a student — it's excluded from their
average rather than treated as a zero. See `sample_data/sample_scores.xlsx`
for a working example (Girija Joshi's actual data from development).

## Editing content without touching code

Everything a non-engineer would want to change lives in `config/`:

| File | What it controls |
|---|---|
| `skill_taxonomy.json` | Which raw-score columns belong to which intelligence. Edit if a grade/school adds or drops an activity. |
| `career_map.json` | The 2-job-per-stream career suggestions per intelligence. Leave a stream's list empty (`[]`) where there's no honest fit — the report shows this as a blank, never a forced filler. |
| `intelligence_meta.json` | The one-line definitions and short keyword phrases used in report copy. |
| `report_config.py` | Tier score thresholds, all colors, brand name/tagline/contact details, the counselor sign-off placeholder. |

## Two rules baked into the code (not just content) — do not remove without discussion

1. **Career grids never appear on a Growth-tier intelligence page.** If a
   student isn't naturally strong in an intelligence, the report doesn't
   suggest careers built on it — see `build_report.py`, `CAREER_GRID_TIERS`
   in `report_config.py`. This was a specific, deliberate fix during
   development after an early draft suggested Chartered Accountancy to a
   student who scored very low on Logical reasoning.
2. **Tier is decided by an internal average that's never displayed.** The
   report always shows individual sub-skill scores, never a blended
   intelligence-level number.

## On the narrative text quality

The current narrative engine (`src/narrative.py`) is rule-based and free
to run at any scale, but it's necessarily less specific than a human (or
AI) reading each student's numbers fresh — it can only say what a template
was written to say. If later on richer, more specific per-student prose
becomes worth the small per-report API cost, that's a contained swap
(same function signatures, different implementation) rather than a rebuild
— worth a conversation if report quality becomes a differentiator you want
to push further.

## Known limitation

Each report section is designed to fit one physical page. If a future
taxonomy change adds enough sub-skills that a section overflows, the extra
content pushes onto a continuation page and the automatic page-numbering
in the Table of Contents can drift by one for that student's report only —
it won't break other students' reports or corrupt anything, but **always
test-render a sample after editing `skill_taxonomy.json`** to confirm
nothing overflows before running a full batch.

## Project structure

```
jagrati_mi_report_generator/
├── generate_reports.py       ← the command you run
├── requirements.txt
├── config/                   ← edit these for content/branding changes
│   ├── skill_taxonomy.json
│   ├── career_map.json
│   ├── intelligence_meta.json
│   └── report_config.py
├── templates/
│   └── report_template.html  ← the actual page design (Jinja2 + CSS)
├── src/
│   ├── data_loader.py        ← reads the Excel
│   ├── scoring.py            ← tiers + top-3
│   ├── narrative.py          ← fills in the report's written content
│   ├── build_report.py       ← assembles everything for one student
│   └── pdf_generator.py      ← renders the final PDF
├── sample_data/
│   └── sample_scores.xlsx    ← Girija Joshi's real data, for testing
└── output/                   ← generated PDFs land here
```
