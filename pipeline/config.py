"""Central paths and configuration.

Everything is resolved relative to the repository root (the parent of this
``pipeline/`` directory), so the pipeline can be run from any working
directory without machine-specific absolute paths.
"""

from __future__ import annotations

from pathlib import Path

# Repository root = the directory that contains ``pipeline/``.
REPO_ROOT = Path(__file__).resolve().parent.parent

CORPUS_DIR = REPO_ROOT / "corpus"
DATA_DIR = REPO_ROOT / "data"
PIPELINE_DIR = REPO_ROOT / "pipeline"

# The raw plain-text corpus file produced by `extract.py` (or provided
# directly by the user). Kept out of version control — see corpus/README.md.
RAW_TEXT_PATH = CORPUS_DIR / "haizi.txt"

# Stopword list (used for the optional general frequency table, not for the
# curated imagery atlas).
STOPWORDS_PATH = PIPELINE_DIR / "stopwords.txt"

# Output JSON files.
IMAGERY_JSON = DATA_DIR / "imagery.json"
COOCCURRENCE_JSON = DATA_DIR / "cooccurrence.json"
POEMS_JSON = DATA_DIR / "poems.json"
STATS_JSON = DATA_DIR / "stats.json"

# ---------------------------------------------------------------------------
# Extract settings
# ---------------------------------------------------------------------------
# Xi Chuan's 《海子诗全集》 (Writer's Publishing House) lays the poems out
# between these pages; the front matter (目录 / preface) and back matter are
# skipped. These are defaults only — override on the command line. Page
# indices are 0-based, matching pdfplumber's ``pdf.pages[start:end]`` slice.
PDF_START_PAGE = 48
PDF_END_PAGE = 872

# ---------------------------------------------------------------------------
# Analysis settings
# ---------------------------------------------------------------------------
# Number of top related-imagery words stored per imagery node.
MAX_RELATED = 12

# How much surrounding text to store alongside each occurrence in
# ``poems.json``. This is a deliberately small excerpt (not the full poem):
# the matched line only, truncated to this many characters. Keeping it short
# is both a copyright courtesy and a way to keep ``data/`` lean.
MAX_EXCERPT_CHARS = 36

# Minimum number of top words to include per poem in ``poems.json``.
TOP_WORDS_PER_POEM = 12

# Imagery nodes with fewer than this many occurrences across the whole corpus
# are still computed but ranked lower; the frontend may hide them by default.
MIN_FREQUENCY = 2

# Years are only recorded when a poem's date line is unambiguous. Poems
# without a reliable date get ``year = null`` and are excluded from the
# timeline, never fabricated.
TIMELINE_MIN_YEAR = 1982
TIMELINE_MAX_YEAR = 1990

# Book sections that are not poetry (Xi Chuan's edition appends Hai Zi's
# literary essays and an addendum of early works). The atlas is about the
# poems, so these sections are excluded from analysis.
EXCLUDED_SECTION_KEYWORDS = ("文论", "补遗")


def ensure_dirs() -> None:
    """Create output directories if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
