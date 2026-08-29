"""Clean raw extracted text into a list of lines.

The PDF extraction is noisy in predictable ways:

  * stanza breaks come through as lines holding a single space,
  * some lines carry full-width spaces (U+3000) as indentation,
  * the odd control character or page-break artifact sneaks in.

This stage normalises that noise while preserving line structure, because the
later segmentation stage relies on line boundaries. It does *not* try to
reconstruct poems — that is ``segmentation``'s job.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from . import config

# A stanza/paragraph separator is a line whose visible content is empty.
_BLANK_LINE = re.compile(r"^\s*$")

# Full-width space and other horizontal whitespace at the start of a line.
_LEADING_WS = re.compile(r"^[\u3000\u00a0 ]+")


def clean_text(raw: str) -> list[str]:
    """Return cleaned, non-empty lines (blank lines kept as ``""`` markers)."""
    lines: list[str] = []
    for line in raw.splitlines():
        # Normalise unusual line-break / control characters.
        line = line.replace("\u200b", "").replace("\xa0", " ")
        line = line.strip()
        lines.append(line)
    return lines


def load_cleaned_lines(path: Path) -> list[str]:
    """Read the raw corpus file and return cleaned lines."""
    raw = path.read_text(encoding="utf-8")
    return clean_text(raw)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Clean the raw corpus text.")
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        default=config.RAW_TEXT_PATH,
        help="Raw text file (default: corpus/haizi.txt).",
    )
    args = parser.parse_args(argv)

    lines = load_cleaned_lines(args.input)
    content = [l for l in lines if l]
    print(f"Cleaned {len(lines)} lines ({len(content)} non-empty) from {args.input}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
