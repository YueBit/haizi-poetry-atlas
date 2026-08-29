"""Co-occurrence: how often imagery words appear in the same poem.

The relationship metric is deliberately simple and transparent:

    score(A, B) = |poems containing A and B|
                  -------------------------------
                  sqrt(|poems containing A| × |poems containing B|)

This is the cosine similarity of the two words' binary presence vectors over
poems (equivalently, the Ochiai coefficient). It ranges from 0 (never
together) to 1 (always together), is symmetric, and is not inflated by either
word's raw frequency. It says nothing about literary meaning — only "these
two images tend to live in the same poems."
"""

from __future__ import annotations

from math import sqrt


def build_edges(words: dict[str, dict]) -> list[dict]:
    """Return co-occurrence edges between imagery words.

    ``words`` is the ``words`` dict from :func:`imagery.analyze`. Edges are
    undirected and emitted once per pair, sorted by score descending.
    """
    edges: list[dict] = []
    word_list = list(words.keys())

    for i, a in enumerate(word_list):
        set_a = set(words[a]["poem_ids"])
        count_a = words[a]["poem_count"]
        for b in word_list[i + 1:]:
            set_b = set(words[b]["poem_ids"])
            inter = len(set_a & set_b)
            if inter == 0:
                continue
            denom = sqrt(count_a * words[b]["poem_count"])
            score = inter / denom if denom else 0.0
            edges.append(
                {"a": a, "b": b, "score": round(score, 4), "cooccur": inter}
            )

    edges.sort(key=lambda e: e["score"], reverse=True)
    return edges


def top_related(edges: list[dict], max_related: int) -> dict[str, list[dict]]:
    """Group edges into ``{word: [{word, score, cooccur}, ...]}`` ranked lists."""
    related: dict[str, list[dict]] = {}
    for edge in edges:
        for src, dst in (("a", "b"), ("b", "a")):
            w = edge[src]
            if w not in related:
                related[w] = []
            related[w].append(
                {"word": edge[dst], "score": edge["score"], "cooccur": edge["cooccur"]}
            )
    for w in related:
        related[w].sort(key=lambda e: e["score"], reverse=True)
        related[w] = related[w][:max_related]
    return related
