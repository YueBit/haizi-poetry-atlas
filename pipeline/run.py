"""Pipeline entry point.

Runs the full ``corpus -> JSON`` flow and writes the four data files::

    python -m pipeline.run

Use ``python -m pipeline.run --help`` for options. Individual stages can also
be run on their own (``python -m pipeline.extract``, ``python -m pipeline.clean``)
for debugging.
"""

from __future__ import annotations

import argparse
import sys

from . import clean, cooccurrence, config, export, imagery, segmentation, timeline


def _date_range(poems: list[dict]) -> tuple[int | None, int | None]:
    years = [p["year"] for p in poems if p.get("year") is not None]
    if not years:
        return None, None
    return min(years), max(years)


def run(corpus_path=None, min_frequency=None, max_related=None) -> tuple[dict, dict]:
    """Run the pipeline and return the analysis bundle + metadata."""
    config.MIN_FREQUENCY = min_frequency if min_frequency is not None else config.MIN_FREQUENCY
    config.MAX_RELATED = max_related if max_related is not None else config.MAX_RELATED

    path = corpus_path or config.RAW_TEXT_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Corpus not found: {path}\n"
            "Run `python -m pipeline.extract` on a PDF, or place a plain-text "
            "corpus at corpus/haizi.txt (see corpus/README.md)."
        )

    raw = path.read_text(encoding="utf-8")
    lines = clean.clean_text(raw)
    poems = segmentation.segment(lines)

    analysis = imagery.analyze(poems)
    analysis["edges"] = cooccurrence.build_edges(analysis["words"])
    analysis["related"] = cooccurrence.top_related(
        analysis["edges"], config.MAX_RELATED
    )
    analysis["by_year"] = timeline.build_timeline(
        analysis["words"], analysis["poems"]
    )

    meta = {
        "poem_count": len(poems),
        "total_chars": sum(len(l) for l in lines if l),
        "date_range": _date_range(analysis["poems"]),
    }
    return analysis, meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m pipeline.run",
        description="Haizi Poetry Atlas — build the static JSON dataset.",
    )
    parser.add_argument(
        "--corpus",
        type=config.REPO_ROOT.joinpath,
        default=config.RAW_TEXT_PATH,
        help="Path to the plain-text corpus (default: corpus/haizi.txt).",
    )
    parser.add_argument(
        "--min-frequency",
        type=int,
        default=config.MIN_FREQUENCY,
        help=f"Drop imagery words below this corpus frequency (default: {config.MIN_FREQUENCY}).",
    )
    parser.add_argument(
        "--max-related",
        type=int,
        default=config.MAX_RELATED,
        help=f"Related-imagery entries kept per word (default: {config.MAX_RELATED}).",
    )
    args = parser.parse_args(argv)

    analysis, meta = run(
        corpus_path=args.corpus,
        min_frequency=args.min_frequency,
        max_related=args.max_related,
    )
    export.export_all(analysis, meta)

    words = analysis["words"]
    top = sorted(words.items(), key=lambda kv: kv[1]["frequency"], reverse=True)[:10]
    print(f"poems:          {meta['poem_count']}")
    print(f"imagery words:  {len(words)}")
    print(f"edges:          {len(analysis['edges'])}")
    print(f"date range:     {meta['date_range'][0]}–{meta['date_range'][1]}")
    print()
    print("top imagery (frequency / poems):")
    for w, s in top:
        print(f"  {w:<6} {s['frequency']:>4}  in {s['poem_count']} poems")
    print()
    print("wrote data/stats.json, imagery.json, cooccurrence.json, poems.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
