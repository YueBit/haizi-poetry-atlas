"""Chinese word segmentation with jieba.

jieba is loaded once and fed a user dictionary built from the curated imagery
lexicon, so that images like 麦地 / 黑夜 / 黎明 are recognised as single
tokens. Only the exact tokens that match the lexicon are of interest to the
atlas; everything else is ignored.
"""

from __future__ import annotations

import jieba

from . import lexicon

_loaded = False


def _ensure_loaded() -> None:
    """Initialise jieba and load the imagery user dictionary (idempotent)."""
    global _loaded
    if _loaded:
        return
    # Quiet jieba's build log; not relevant to this pipeline.
    jieba.setLogLevel(60)
    for word in lexicon.LEXICON:
        # A high freq tells jieba to prefer this multi-character reading.
        jieba.add_word(word, freq=200000)
    _loaded = True


def tokenize_line(line: str) -> list[str]:
    """Tokenize one line into jieba words (all tokens, not just imagery)."""
    _ensure_loaded()
    return list(jieba.cut(line.strip(), cut_all=False))


def imagery_tokens(line: str) -> list[str]:
    """Return the lexicon imagery words present in a line, in order.

    A word that appears twice in the line is returned twice, so callers can
    sum lengths for a true frequency count.
    """
    _ensure_loaded()
    lexicon_set = lexicon.LEXICON  # dict -> membership by key
    return [tok for tok in tokenize_line(line) if tok in lexicon_set]
