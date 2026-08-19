"""
Reads the SCALED SCORES workbook — one row per student, scores already
converted to the 0-10 scale (your team's existing tool has already done
the raw-to-scaled conversion before this file is produced).

Required columns: Name, Class, School
Plus one column per activity, named exactly as it appears in
config/skill_taxonomy.json (e.g. "Problem Solving", "Dexterity", "Diction"...).
Column names are matched case-insensitively and ignore extra spaces, so
"problem solving" and "Problem Solving " both work.

If a student wasn't assessed on a particular activity, leave that cell
blank — it will be excluded from that student's intelligence average
rather than treated as a zero.
"""

import json
import math
from pathlib import Path
import pandas as pd

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def load_skill_taxonomy() -> dict:
    """Returns {skill_name: intelligence_name}, built from skill_taxonomy.json."""
    with open(CONFIG_DIR / "skill_taxonomy.json") as f:
        raw = json.load(f)
    taxonomy = {}
    for intelligence, skills in raw.items():
        if intelligence.startswith("_"):
            continue
        for skill in skills:
            taxonomy[_normalize(skill)] = intelligence
    return taxonomy


def _normalize(name: str) -> str:
    return " ".join(str(name).strip().split()).lower()


def load_students(scaled_scores_path: str) -> list[dict]:
    """
    Returns a list of student records:
    [{"name": ..., "class": ..., "school": ..., "scores": {skill_name: scaled_score, ...}}, ...]

    Only columns recognised in skill_taxonomy.json are read as scores.
    Unrecognised columns are ignored, with a printed warning so nothing is
    silently dropped without you knowing — this is the main thing to check
    if a report comes out with an intelligence missing unexpectedly.
    """
    taxonomy = load_skill_taxonomy()
    df = pd.read_excel(scaled_scores_path)
    df.columns = [str(c).strip() for c in df.columns]

    id_cols = {"name", "class", "school"}
    score_cols = [c for c in df.columns if _normalize(c) not in id_cols]

    unrecognised = [c for c in score_cols if _normalize(c) not in taxonomy]
    if unrecognised:
        print(f"[warning] These columns aren't in skill_taxonomy.json and will be skipped: {unrecognised}")
    recognised_cols = [c for c in score_cols if _normalize(c) in taxonomy]
    if not recognised_cols:
        raise ValueError("No recognised score columns found. Check column names against "
                          "config/skill_taxonomy.json (they must match exactly, case-insensitive).")

    name_col = next((c for c in df.columns if _normalize(c) == "name"), None)
    class_col = next((c for c in df.columns if _normalize(c) == "class"), None)
    school_col = next((c for c in df.columns if _normalize(c) == "school"), None)
    if not name_col:
        raise ValueError("Couldn't find a 'Name' column in the scores workbook.")

    students = []
    for _, row in df.iterrows():
        scores = {}
        for col in recognised_cols:
            val = row[col]
            if val is None or (isinstance(val, float) and math.isnan(val)):
                continue  # not administered — excluded, not treated as zero
            scores[col] = float(val)

        students.append({
            "name": str(row[name_col]).strip(),
            "class": str(row[class_col]).strip() if class_col else "",
            "school": str(row[school_col]).strip() if school_col else "",
            "scores": scores,
        })
    return students
