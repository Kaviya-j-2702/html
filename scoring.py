"""
Turns a student's flat {skill: scaled_score} dict into the structured
per-intelligence data the report template needs: sub-skill scores grouped
by intelligence, an internal (never-displayed) average used only to assign
a tier, and the top-N intelligences for the combined page.
"""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "config"))
from report_config import STANDOUT_MIN, DEVELOPING_MIN, TOP_N  # noqa: E402

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def _load_taxonomy():
    with open(CONFIG_DIR / "skill_taxonomy.json") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def tier_for_average(avg: float) -> str:
    if avg >= STANDOUT_MIN:
        return "Standout"
    if avg >= DEVELOPING_MIN:
        return "Developing"
    return "Growth"


def score_student(student: dict) -> dict:
    """
    Input: {"name", "class", "school", "scores": {skill: scaled_score}}
    Output: adds "intelligences": {
        intelligence_name: {
            "sub_skills": [(skill, score), ...] sorted high to low,
            "internal_avg": float,   # never shown in the report
            "tier": "Standout" | "Developing" | "Growth",
        }, ...
    }, "top_n": [intelligence_name, ...] sorted by internal_avg desc
    Intelligences with no scores for this student (e.g. Naturalist, or an
    activity not administered) are skipped entirely.
    """
    taxonomy = _load_taxonomy()
    scores = student["scores"]

    intelligences = {}
    for intelligence_name, skill_list in taxonomy.items():
        sub_scores = [(skill, scores[skill]) for skill in skill_list if skill in scores]
        if not sub_scores:
            continue  # not administered / not part of this assessment
        avg = sum(s for _, s in sub_scores) / len(sub_scores)
        intelligences[intelligence_name] = {
            "sub_skills": sorted(sub_scores, key=lambda x: -x[1]),
            "internal_avg": round(avg, 3),
            "tier": tier_for_average(avg),
        }

    ranked = sorted(intelligences.keys(), key=lambda i: -intelligences[i]["internal_avg"])
    top_n = ranked[:TOP_N]

    result = dict(student)
    result["intelligences"] = intelligences
    result["ranked_intelligences"] = ranked
    result["top_n"] = top_n
    return result
