"""Timeline: how imagery frequency changes year over year.

Only poems with a reliable ``year`` contribute. Poems that could not be dated
are silently excluded from the timeline — never guessed. The output is a
``{word: {year: count}}`` map of raw occurrence counts, which the frontend
normalises as it sees fit.
"""

from __future__ import annotations

from collections import defaultdict


def build_timeline(
    words: dict[str, dict], poems: list[dict]
) -> dict[str, dict[int, int]]:
    """Return ``{word: {year: occurrence_count}}`` for dated poems only."""
    by_year: dict[str, dict[int, int]] = {w: defaultdict(int) for w in words}

    for poem in poems:
        year = poem.get("year")
        if year is None:
            continue
        for word, count in poem.get("imagery", {}).items():
            if word in by_year:
                by_year[word][year] += count

    return {w: dict(sorted(d.items())) for w, d in by_year.items()}
