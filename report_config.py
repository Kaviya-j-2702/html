"""
Central, editable settings for the report generator.
Change thresholds/colors/copy here — nothing else in the codebase should
need touching for a normal content or branding tweak.
"""

# ---- Tier thresholds (based on each intelligence's INTERNAL average of its
#      own sub-skills — this average is never shown to the reader, it only
#      decides which tier/depth a page gets) ----
STANDOUT_MIN = 7.0
DEVELOPING_MIN = 4.0
# below DEVELOPING_MIN = Growth area

TIER_COLORS = {
    "Standout":   {"band": "#6C4CE0", "text": "#6C4CE0", "bar": "#6C4CE0", "box_bg": "#F6F3FF"},
    "Developing": {"band": "#2F8FE0", "text": "#2F8FE0", "bar": "#2F8FE0", "box_bg": "#EEF6FF"},
    "Growth":     {"band": "#E0972F", "text": "#C97B0E", "bar": "#E0972F", "box_bg": "#FFF8EC"},
}

TIER_LABELS = {
    "Standout": "Standout strength",
    "Developing": "Developing",
    "Growth": "Growth area",
}

# Number of top intelligences combined on the final "bigger picture" page
TOP_N = 3

# Career grids are only shown for these tiers. Growth-tier intelligences
# never get career suggestions built on them.
CAREER_GRID_TIERS = {"Standout", "Developing"}

# Streams shown in every career grid, in this order, with their card colors
STREAMS = ["Science", "Commerce", "Arts", "Others"]
STREAM_COLORS = {
    "Science":  {"bg": "#F0ECFF", "label": "#4E36A8"},
    "Commerce": {"bg": "#EEF6FF", "label": "#1D5F9C"},
    "Arts":     {"bg": "#FFF1E8", "label": "#B25A1E"},
    "Others":   {"bg": "#FFF8EC", "label": "#8A5A00"},
}

# Report branding
BRAND_NAME = "JAGRATI"
BRAND_TAGLINE = "Shaping the true you"
BRAND_WEBSITE = "jagratiedu.com"
BRAND_EMAIL = "info@jagratiedu.com"
BRAND_PHONE = "+91 96062 58596"
PROGRAM_NAME = "Career Mapping Program"
COUNSELOR_SIGNOFF_NAME = "[ Counselor name ]"
