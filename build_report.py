"""
Builds the full render context for ONE student and renders their PDF.
This is where every rule locked in during development is enforced in code:

  - Career grids only appear for Standout / Developing intelligences
    (config.CAREER_GRID_TIERS) — Growth-tier pages get the honest
    "not listing careers here" note instead.
  - Career lists are read as-is from config/career_map.json, including
    genuinely empty stream lists — the template renders those as an
    honest blank, never a fabricated filler career.
  - The combined top-3 page's career grid is built from the union of the
    top 3 intelligences' own career maps (weighted toward jobs that show
    up under more than one of the three), not hand-authored per student.
  - Tier is decided by an internal average that is NEVER shown in the
    report itself — only sub-skill-level scores are displayed.
"""

import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "config"))
import report_config as cfg  # noqa: E402

from scoring import score_student  # noqa: E402
import narrative  # noqa: E402

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _load_json(name):
    with open(CONFIG_DIR / name) as f:
        return json.load(f)


def _first_name(full_name: str) -> str:
    return full_name.strip().split(" ")[0] if full_name.strip() else full_name


def _build_career_grid(intelligence_name: str, career_map: dict) -> dict:
    return {stream: list(career_map.get(intelligence_name, {}).get(stream, []))
            for stream in cfg.STREAMS}


def _build_combined_careers(top_n_names: list, career_map: dict) -> dict:
    """Union of the top-N intelligences' career lists per stream, jobs that
    appear under more than one of the top-N intelligences are preferred."""
    result = {}
    for stream in cfg.STREAMS:
        seen_order = []
        freq = {}
        for intel_name in top_n_names:
            for job in career_map.get(intel_name, {}).get(stream, []):
                if job not in freq:
                    seen_order.append(job)
                freq[job] = freq.get(job, 0) + 1
        ranked = sorted(seen_order, key=lambda j: -freq[j])
        result[stream] = ranked[:2]
    return result


def build_context(student_raw: dict) -> dict:
    """student_raw: {"name", "class", "school", "scores": {skill: scaled_score}}"""
    career_map = _load_json("career_map.json")
    intelligence_meta = _load_json("intelligence_meta.json")

    student_scored = score_student(student_raw)
    first_name = _first_name(student_scored["name"])
    intelligences = student_scored["intelligences"]
    ranked = student_scored["ranked_intelligences"]
    top_n = student_scored["top_n"]

    # ---- Snapshot page: group by tier, preserving rank order within tier ----
    snapshot_tiers = []
    for tier_name in ["Standout", "Developing", "Growth"]:
        tier_list = [
            {"name": name, "sub_skills": intelligences[name]["sub_skills"]}
            for name in ranked if intelligences[name]["tier"] == tier_name
        ]
        snapshot_tiers.append((tier_name, tier_list))

    # ---- Individual intelligence pages (page numbers computed after we know the count) ----
    intelligence_pages = []
    for name in ranked:
        data = intelligences[name]
        tier = data["tier"]
        sub_skills = data["sub_skills"]
        meta = intelligence_meta.get(name, {"definition": "", "keyword_phrase": name})
        show_career_grid = tier in cfg.CAREER_GRID_TIERS

        page = {
            "name": name,
            "tier": tier,
            "definition": meta["definition"],
            "sub_skills": sub_skills,
            "band_subtitle": narrative.band_subtitle(name, sub_skills, tier).format(
                student_first_name=first_name),
            "what_this_tells_us": narrative.what_this_tells_us(name, sub_skills, tier, first_name),
            "recommendation": narrative.recommendation(name, sub_skills, tier, first_name),
            "show_career_grid": show_career_grid,
        }
        if show_career_grid:
            grid = _build_career_grid(name, career_map)
            page["careers"] = grid
            page["stream_bg"] = {s: cfg.STREAM_COLORS[s]["bg"] for s in cfg.STREAMS}
            page["stream_label_color"] = {s: cfg.STREAM_COLORS[s]["label"] for s in cfg.STREAMS}
        intelligence_pages.append(page)

    # ---- Page numbering ----
    PAGE_COVER, PAGE_TOC, PAGE_ABOUT, PAGE_SNAPSHOT = 1, 2, 3, 4
    first_intel_page = 5
    for i, page in enumerate(intelligence_pages):
        page["page_number"] = first_intel_page + i
    combined_page_number = first_intel_page + len(intelligence_pages)
    signoff_page_number = combined_page_number + 1

    # ---- TOC ----
    toc_entries = [
        {"title": "About this report", "page": PAGE_ABOUT, "tier": None},
        {"title": "Your smart map", "page": PAGE_SNAPSHOT, "tier": None},
    ]
    for page in intelligence_pages:
        toc_entries.append({
            "title": f"{page['name']} Intelligence",
            "page": page["page_number"],
            "tier": cfg.TIER_LABELS[page["tier"]].split()[0],  # "Standout" / "Developing" / "Growth"
            "tier_color": cfg.TIER_COLORS[page["tier"]]["band"],
        })
    toc_entries.append({"title": "Where the top intelligences meet", "page": combined_page_number, "tier": None})
    toc_entries.append({"title": "Closing note", "page": signoff_page_number, "tier": None})

    # ---- Combined top-N page ----
    combined_narrative_text = narrative.combined_narrative(top_n, intelligence_meta, first_name)
    combined_careers = _build_combined_careers(top_n, career_map)

    context = {
        "brand": {
            "name": cfg.BRAND_NAME,
            "tagline": cfg.BRAND_TAGLINE,
            "website": cfg.BRAND_WEBSITE,
            "email": cfg.BRAND_EMAIL,
            "phone": cfg.BRAND_PHONE,
            "program_name": cfg.PROGRAM_NAME,
            "counselor_signoff": cfg.COUNSELOR_SIGNOFF_NAME,
        },
        "student": {
            "name": student_scored["name"],
            "first_name": first_name,
            "class": student_scored["class"],
            "school": student_scored["school"],
        },
        "generated_date": date.today().strftime("%d %b %Y"),
        "toc_entries": toc_entries,
        "snapshot_tiers": snapshot_tiers,
        "tier_colors": cfg.TIER_COLORS,
        "tier_labels": cfg.TIER_LABELS,
        "intelligence_pages": intelligence_pages,
        "streams": cfg.STREAMS,
        "top_n": top_n,
        "combined_narrative_text": combined_narrative_text,
        "combined_careers": combined_careers,
        "combined_stream_bg": {s: cfg.STREAM_COLORS[s]["bg"] for s in cfg.STREAMS},
        "combined_stream_label_color": {s: cfg.STREAM_COLORS[s]["label"] for s in cfg.STREAMS},
        "combined_page_number": combined_page_number,
        "signoff_page_number": signoff_page_number,
    }
    return context
