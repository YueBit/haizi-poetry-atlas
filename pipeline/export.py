"""Assemble and write the static JSON the web frontend consumes.

Four files are written into ``data/``:

  * ``stats.json``        — corpus-level numbers and methodology notes;
  * ``imagery.json``      — imagery nodes (frequency, poems, related, by_year);
  * ``cooccurrence.json`` — the graph edges;
  * ``poems.json``        — poem records with limited occurrence excerpts.

JSON is written with UTF-8 and ``ensure_ascii=False`` so the Chinese text is
human-readable, and with sorted keys for a stable, diff-friendly output.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import config, lexicon


def _write_json(path: Path, obj: object) -> None:
    config.ensure_dirs()
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False),
        encoding="utf-8",
    )


def build_stats(
    analysis: dict,
    poem_count: int,
    total_chars: int,
    date_range: tuple[int | None, int | None],
) -> dict:
    words = analysis["words"]
    top = sorted(
        words.items(), key=lambda kv: kv[1]["frequency"], reverse=True
    )[:30]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "title": "海子诗歌图谱 · Haizi Poetry Atlas",
        "corpus": {
            "name": "海子诗全集（西川 编）",
            "poem_count": poem_count,
            "total_characters": total_chars,
            "date_range": {"min": date_range[0], "max": date_range[1]},
            "note": (
                "Poem boundaries, titles, and years are extracted best-effort "
                "from a PDF text export; see README for known limitations."
            ),
        },
        "imagery_word_count": len(words),
        "top_words": [
            {"word": w, "frequency": s["frequency"],
             "poem_count": s["poem_count"]}
            for w, s in top
        ],
        "methodology": {
            "tokenizer": "jieba with a curated imagery user-dictionary",
            "cooccurrence": (
                "cosine similarity of binary poem-presence vectors "
                "(Ochiai coefficient): |A∩B| / sqrt(|A|·|B|)"
            ),
            "timeline": "occurrence counts by poem year; undated poems excluded",
            "excerpt": (
                f"occurrences store the matched line clipped to "
                f"~{config.MAX_EXCERPT_CHARS} chars — limited excerpts, not "
                f"full poems"
            ),
        },
    }


def build_imagery(analysis: dict) -> list[dict]:
    words = analysis["words"]
    related = analysis["related"]
    by_year = analysis["by_year"]
    nodes = []
    for word, stats in words.items():
        nodes.append(
            {
                "word": word,
                "theme": stats["theme"],
                "theme_label": lexicon.THEME_LABELS.get(stats["theme"], stats["theme"]),
                "frequency": stats["frequency"],
                "poem_count": stats["poem_count"],
                "poem_ids": stats["poem_ids"],
                "by_year": by_year.get(word, {}),
                "related": related.get(word, []),
            }
        )
    nodes.sort(key=lambda n: n["frequency"], reverse=True)
    return nodes


def build_poems(analysis: dict) -> list[dict]:
    return analysis["poems"]


def build_cooccurrence(analysis: dict) -> list[dict]:
    return analysis["edges"]


def export_all(analysis: dict, meta: dict) -> None:
    """Write the four JSON files from a completed analysis bundle."""
    _write_json(config.STATS_JSON, build_stats(
        analysis, meta["poem_count"], meta["total_chars"], meta["date_range"]
    ))
    _write_json(config.IMAGERY_JSON, build_imagery(analysis))
    _write_json(config.POEMS_JSON, build_poems(analysis))
    _write_json(config.COOCCURRENCE_JSON, build_cooccurrence(analysis))
