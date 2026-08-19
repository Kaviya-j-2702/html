"""
Generates the report's narrative text for one intelligence, or for the
combined top-3 page, WITHOUT calling any external AI service — pure
templated Python, deterministic, free to run at any scale.

Every sentence pattern here encodes the rules locked in during development:
  - This is an INNATE ability measure. Low scores are described as "less
    natural", never as "hasn't been practiced" or "flat".
  - Depth and register scale with tier (Standout > Developing > Growth).
  - Growth-tier intelligences never get career suggestions built on them —
    that's enforced in build_report.py, not here, but the language here is
    written to be consistent with that rule.

If you'd rather have richer, more specific prose per student (closer to
what a human writer would produce), see narrative_ai.py for a drop-in
replacement that calls the Claude API instead — same function signature,
so build_report.py doesn't need to change either way.
"""

import hashlib


def _variant(seed_text: str, n: int) -> int:
    """Deterministic pseudo-random index 0..n-1, stable for a given student+intelligence
    so re-running the generator produces identical reports, but different students
    get some variety in phrasing rather than 100 identical sentences."""
    h = hashlib.md5(seed_text.encode()).hexdigest()
    return int(h, 16) % n


def band_subtitle(intelligence: str, sub_skills: list, tier: str) -> str:
    """The short factual line shown in the coloured band header."""
    top_skill, top_score = sub_skills[0]
    if tier == "Growth":
        low = [f"{s} ({v:g}/10)" for s, v in sub_skills]
        return (f"{', '.join(low)} — the intelligence furthest from where "
                f"{{student_first_name}}'s natural strengths lie.")
    if tier == "Standout":
        rest = sub_skills[1:]
        if rest:
            rest_txt = " and ".join(f"{s} ({v:g}/10)" for s, v in rest)
            return (f"The clearest natural signal in the assessment: "
                    f"{top_score:g}/10 on {top_skill}, alongside {rest_txt}.")
        return f"A clear natural signal: {top_score:g}/10 on {top_skill}."
    # Developing
    low_skill, low_score = sub_skills[-1]
    return (f"{top_skill} ({top_score:g}/10) is the more natural pull here; "
            f"{low_skill} ({low_score:g}/10) is a smaller part of the same picture.")


def what_this_tells_us(intelligence: str, sub_skills: list, tier: str, student_first_name: str) -> str:
    top_skill, top_score = sub_skills[0]
    low_skill, low_score = sub_skills[-1]
    spread = top_score - low_score

    if tier == "Standout":
        variants = [
            (f"{top_skill} points to an unmistakable natural gift in this area. "
             + (f"{low_skill} sits lower, still a real ability, just a less dominant "
                f"part of the same natural strength."
                if spread >= 3 else
                f"{student_first_name} is consistently strong across everything measured here.")),
            (f"A standout result — {top_skill} in particular shows a clear, natural pull. "
             + (f"{low_skill} is comparatively more moderate, though still part of an "
                f"overall genuine strength."
                if spread >= 3 else
                "The strength holds consistently across every sub-skill measured.")),
        ]
        return variants[_variant(student_first_name + intelligence, len(variants))]

    if tier == "Developing":
        variants = [
            (f"{top_skill} is a genuine natural strength on its own. {low_skill} is "
             f"considerably less natural for {student_first_name} by comparison — "
             f"worth reading precisely, since the gift here sits specifically in "
             f"{top_skill.lower()} rather than spread evenly across this intelligence."
             if spread >= 4 else
             f"A steady, moderate natural inclination here, without a sharp peak in "
             f"either direction — {top_skill} and {low_skill} sit close together."),
        ]
        return variants[_variant(student_first_name + intelligence, len(variants))]

    # Growth
    variants = [
        (f"Consistently low scores across {', '.join(s for s, _ in sub_skills)} suggest "
         f"{intelligence.lower()} thinking isn't where {student_first_name}'s natural "
         f"inclination lies right now. That's information about the natural profile, "
         f"not a reflection of effort during the assessment."),
        (f"This result suggests {intelligence.lower()} isn't a natural inclination for "
         f"{student_first_name} at the moment. That says nothing about effort or "
         f"attentiveness — it's simply where this profile currently sits."),
    ]
    return variants[_variant(student_first_name + intelligence, len(variants))]


def recommendation(intelligence: str, sub_skills: list, tier: str, student_first_name: str) -> str:
    top_skill, _ = sub_skills[0]

    if tier == "Standout":
        return (f"This is a natural strength, so building on it plays to an existing "
                f"inclination rather than starting from scratch. Structured, hands-on "
                f"practice in activities that draw on {top_skill.lower()} will compound "
                f"an area {student_first_name} is already naturally strong in.")

    if tier == "Developing":
        return (f"Because this intelligence is present but not dominant, regular — not "
                f"intensive — practice is enough to round it out. Activities that lean on "
                f"{top_skill.lower()} specifically are the most natural entry point.")

    # Growth
    return (f"Because this isn't a natural strength, building it will call for sustained, "
            f"deliberate effort rather than coming easily. That's a reasonable thing to "
            f"work on by choice — it just won't be {student_first_name}'s most natural mode.")


def combined_narrative(top_n_names: list, intelligence_meta: dict, student_first_name: str) -> str:
    """Builds the 'bigger picture' paragraph for the top-3-combined page."""
    phrases = [intelligence_meta[name]["keyword_phrase"] for name in top_n_names]
    listed = ", ".join(phrases[:-1]) + f", and {phrases[-1]}" if len(phrases) > 1 else phrases[0]
    named = ", ".join(top_n_names[:-1]) + f", and {top_n_names[-1]}" if len(top_n_names) > 1 else top_n_names[0]
    return (f"On their own: {listed}. Together, {named} describe someone whose natural "
            f"strengths reinforce each other rather than pulling in different directions. "
            f"That combination is worth reading as one picture, the same way our "
            f"counsellors reason about it in a real session, rather than as three separate "
            f"scores.")
