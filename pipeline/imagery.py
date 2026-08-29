"""Imagery analysis: per-poem and per-word statistics.

For every poem, the body is tokenized with jieba (see ``tokenize``) and the
lines are scanned for lexicon imagery words. Two things are produced:

  * ``imagery`` — a ``{word: count}`` map (count = number of occurrences in
    the poem, including repeats);
  * ``occurrences`` — a short excerpt per ``(word, line)`` pair, so the web
    explorer can take the reader from a statistic back to the poem itself.

The excerpt is deliberately tiny — the matched line, clipped around the word —
so that the published data holds "limited text excerpts" rather than the full
poems (see README § copyright).
"""

from __future__ import annotations

from collections import defaultdict

from . import config, lexicon, tokenize
from .segmentation import Poem


def excerpt(line: str, word: str, max_chars: int = config.MAX_EXCERPT_CHARS) -> str:
    """Return a short context snippet of ``line`` centred on ``word``."""
    idx = line.find(word)
    if idx == -1:
        return line[:max_chars] + ("…" if len(line) > max_chars else "")
    half = max_chars // 2
    start = max(0, idx - half)
    end = min(len(line), idx + len(word) + half)
    snippet = line[start:end]
    if start > 0:
        snippet = "…" + snippet
    if end < len(line):
        snippet = snippet + "…"
    return snippet


def analyze_poem(poem: Poem) -> dict:
    """Return ``{imagery, occurrences}`` for a single poem."""
    imagery: dict[str, int] = defaultdict(int)
    occurrences: list[dict] = []
    seen: set[tuple[str, int]] = set()

    for line_no, line in enumerate(poem.body):
        tokens = tokenize.imagery_tokens(line)
        for word in tokens:
            imagery[word] += 1
            key = (word, line_no)
            if key not in seen:
                seen.add(key)
                occurrences.append(
                    {"word": word, "line": line_no, "text": excerpt(line, word)}
                )

    return {
        "imagery": dict(imagery),
        "occurrences": occurrences,
    }


def analyze(poems: list[Poem]) -> dict:
    """Aggregate imagery across poems.

    Returns::

        {
          "words":  {word: {"frequency", "poem_count", "poem_ids", "theme"}},
          "poems":  [{id, title, year, date, section, imagery, occurrences}],
        }
    """
    word_freq: dict[str, int] = defaultdict(int)
    word_poems: dict[str, list[str]] = defaultdict(list)

    poem_records: list[dict] = []
    for i, poem in enumerate(poems, start=1):
        pid = f"p{i:04d}"
        result = analyze_poem(poem)
        poem_records.append(
            {
                "id": pid,
                "title": poem.title,
                "year": poem.year,
                "date": poem.date,
                "section": poem.section,
                "line_count": len(poem.body),
                "imagery": result["imagery"],
                "occurrences": result["occurrences"],
            }
        )
        for word in result["imagery"]:
            word_freq[word] += result["imagery"][word]
            word_poems[word].append(pid)

    words: dict[str, dict] = {}
    for word in lexicon.LEXICON:
        freq = word_freq.get(word, 0)
        if freq < config.MIN_FREQUENCY:
            continue
        words[word] = {
            "frequency": freq,
            "poem_count": len(word_poems[word]),
            "poem_ids": sorted(word_poems[word]),
            "theme": lexicon.LEXICON[word],
        }

    return {"words": words, "poems": poem_records}
