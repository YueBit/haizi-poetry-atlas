"""Extract plain text from a source PDF.

This stage reproduces the very first step of the original experiment: turn a
PDF of Hai Zi's poetry into a UTF-8 plain-text file. It is optional — if you
already have a plain-text corpus, place it at ``corpus/haizi.txt`` and skip
straight to ``clean``.

Page selection is configurable because the useful content (the poems) usually
lives between the table of contents / preface and any appendix. The defaults
in ``config.py`` are tuned for Xi Chuan's 《海子诗全集》.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import config


def extract_text(pdf_path: Path, start: int, end: int) -> str:
    """Return the concatenated text of PDF pages ``start .. end`` (0-based)."""
    try:
        import pdfplumber
    except ImportError as exc:  # pragma: no cover - dependency-only branch
        raise SystemExit(
            "pdfplumber is required for PDF extraction.\n"
            "Install it with:  pip install pdfplumber\n"
            "Or place a plain-text corpus at corpus/haizi.txt and skip this step."
        ) from exc

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    chunks: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        pages = pdf.pages[start:end]
        for page in pages:
            text = page.extract_text() or ""
            chunks.append(text)
    # Separate pages with a blank line so page boundaries don't merge lines.
    return "\n\n".join(chunks)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Extract plain text from a poetry PDF."
    )
    parser.add_argument(
        "pdf",
        nargs="?",
        type=Path,
        default=None,
        help="Path to the PDF (default: first *.pdf found in corpus/).",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=config.PDF_START_PAGE,
        help=f"First page to include, 0-based (default: {config.PDF_START_PAGE}).",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=config.PDF_END_PAGE,
        help=f"First page to exclude, 0-based (default: {config.PDF_END_PAGE}).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=config.RAW_TEXT_PATH,
        help="Output text file (default: corpus/haizi.txt).",
    )
    args = parser.parse_args(argv)

    pdf_path = args.pdf
    if pdf_path is None:
        candidates = sorted(config.CORPUS_DIR.glob("*.pdf"))
        if not candidates:
            parser.error(
                "No PDF given and none found in corpus/. "
                "Pass a path or drop a PDF into corpus/."
            )
        pdf_path = candidates[0]

    text = extract_text(pdf_path, args.start, args.end)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    print(f"Wrote {len(text)} characters to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
