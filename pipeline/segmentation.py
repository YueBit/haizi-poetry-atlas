"""Poem segmentation.

Splits the cleaned line stream into poems. This is *best-effort*: the source
text was produced by PDF extraction, which merges some line pairs (notably a
poem's closing date with the next poem's title). The segmenter leans on two
reliable signals:

  * date lines — ``1984.4``, ``1985.7.12``, ``1988.6.8—10`` — which mark the
    end of a poem, and
  * the fact that the text merged onto the end of a date or footnote line is
    usually the *next* poem's title.

Titles and years are only recorded when they can be read unambiguously;
poems that cannot be dated get ``year = None`` and are excluded from the
timeline rather than guessed. The README documents the residual limitations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from . import config

# A date line. Formats seen in the corpus:
#   "1984.4", "1985.7.12", "1988.6.8—10", "1984.10(1)"   (year.month[.day])
#   "1983", "1984"                                       (year only — early works)
#   "1984～1985", "1984.6～9", "1988.11.11～20"           (date ranges)
# Each may be followed by trailing text that is actually the next poem's
# title or a section header (e.g. "1984.6新娘", "1983农耕民族",
# "1989.2.2第四编　太阳·七部书").
_DATE_RE = re.compile(
    r"^(?P<date>\d{4}(?:\.\d{1,2}(?:\.\d{1,2})?)?(?:[—–-]\d{1,2})?"
    r"(?:～\d{1,4}(?:\.\d{1,2}(?:\.\d{1,2})?)?)?(?:\([^)]*\))?)"
    r"(?P<tail>.*)$"
)

# Editor's footnotes start with a numbered marker, or are continuations
# beginning with the marker word itself.
_FOOTNOTE_START_RE = re.compile(r"^\(\d+\)")
_FOOTNOTE_CONT_RE = re.compile(r"^编者注")

# Book section headers: 第二编　长诗, 第三编　短诗, 第四编　太阳·七部书 …
_SECTION_RE = re.compile(r"第[一二三四五六七八九十百]+编")

# A horizontal rule used to separate a poem from its footnotes.
_SEPARATOR_RE = re.compile(r"^[—–\-_=·]{3,}$")


@dataclass
class Poem:
    title: str
    body: list[str] = field(default_factory=list)
    date: str | None = None
    year: int | None = None
    section: str | None = None


def _is_footnote(line: str) -> bool:
    return bool(_FOOTNOTE_START_RE.match(line) or _FOOTNOTE_CONT_RE.match(line))


def _title_after_footnote(line: str) -> str | None:
    """If a footnote line ends with ``——编者注。`` + a title, return the title."""
    idx = line.rfind("编者注")
    if idx == -1:
        return None
    tail = line[idx + len("编者注"):].lstrip("。．. ").strip()
    if not tail or tail.startswith("("):
        return None
    return tail


def _split_section(text: str) -> tuple[str, str | None]:
    """Split an embedded section header off the end of ``text``.

    Returns ``(before, section)`` where ``section`` is ``None`` if no header
    is present.
    """
    m = _SECTION_RE.search(text)
    if not m:
        return text, None
    return text[:m.start()].strip(), text[m.start():].strip()


# Characters that follow 改 in legitimate compounds (改变/改造/改革/改写/改正…),
# so we do not strip 改 from a real title such as 《改造两块石头》.
_CHANGE_FOLLOWERS = "了变造革写编成为动换过善良进天日名道组城府朝正期"

# A title that normalises to nothing but a footnote marker.
_FOOTNOTE_ONLY_RE = re.compile(r"^\(\d+\)$")

# A title that is just a bare year (a date fragment that survived).
_BARE_YEAR_RE = re.compile(r"^\d{4}$")


def _strip_revision_marker(title: str) -> str:
    """Strip Xi Chuan's manuscript revision markers from a title.

    A date such as ``1987.7.14改黎明：一首小诗`` means 《黎明：一首小诗》 was
    revised on 1987.7.14; the marker (改 / 再改 / 删 / 三稿 / 修改 …) and any
    time-of-day that trails the date ("夜改四姐妹", "凌晨3点～4点…") are
    editorial noise for the atlas, so they are removed.
    """
    # Date remnants in 年月日 form ("年11月21日诗神降临" -> "诗神降临").
    title = re.sub(r"^年?\d{1,2}月\d{1,2}日", "", title)
    # Stray 年 / punctuation left over from "YYYY年，" dates
    # ("年，我和他和太阳" -> "我和他和太阳").
    title = re.sub(r"^年(?=[，、．。])", "", title)
    title = title.lstrip("，、．。 ")

    # A multi-date prefix: keep only the last segment
    # ("；1985改；1986再改九盏灯（组诗）" -> "1986再改九盏灯（组诗）").
    if "；" in title:
        title = title.rsplit("；", 1)[-1]

    # A bare leading date that got merged onto the title ("1987秋日山谷").
    title = re.sub(r"^\d{4}(?:\.\d{1,2})?(?:\.\d{1,2})?", "", title)

    # An uncertainty marker and a partial month.day ("（？）1.14日落…").
    title = re.sub(r"^（[？?]）", "", title)
    title = re.sub(r"^\d{1,2}\.\d{1,2}", "", title)

    # Trailing time-of-day, part of the date ("凌晨3点～4点太平洋上的贾宝玉").
    title = re.sub(r"^(?:凌晨|清晨|午后|傍晚)\d{0,2}点?(?:～\d{0,2}点?)?", "", title)

    # Unambiguous revision markers, longest first ("夜改" = date "…夜" + 改).
    for marker in ("夜再改", "夜改", "再改", "三改", "三稿", "二稿", "四稿", "五稿", "修改"):
        if title.startswith(marker):
            return title[len(marker):].lstrip("：: ")

    # Bare 改 (with compound guard) and 删.
    if title.startswith("改") and len(title) > 1 and title[1] not in _CHANGE_FOLLOWERS:
        return title[1:].lstrip("：: ")
    if title.startswith("删"):
        return title[1:].lstrip("：: ")

    return title


def _normalise_title(title: str) -> str:
    title = title.strip().lstrip("。．.、 ").rstrip("。．. ")
    return _strip_revision_marker(title)


def segment(lines: list[str]) -> list[Poem]:
    """Segment cleaned lines into a list of :class:`Poem` objects."""
    poems: list[Poem] = []
    current: Poem | None = None
    pending_title: str | None = None
    section: str | None = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if _SEPARATOR_RE.match(line):
            continue

        # --- editor's footnote ---
        if _is_footnote(line):
            title = _title_after_footnote(line)
            if title:
                before, sec = _split_section(title)
                if sec:
                    section = sec
                    if before:
                        pending_title = before
                else:
                    pending_title = title
            continue

        # --- date line (closes the current poem) ---
        m = _DATE_RE.match(line)
        if m:
            date_str, tail = m.group("date"), m.group("tail").strip()
            year = int(date_str[:4])
            if current is not None:
                current.date = date_str
                current.year = year
            if tail:
                before, sec = _split_section(tail)
                if sec:
                    section = sec
                    if before:
                        pending_title = before
                else:
                    pending_title = tail
            if current is not None:
                poems.append(current)
                current = None
            continue

        # --- section header, possibly embedded in a body line ---
        body_part, sec = _split_section(line)
        if sec:
            section = sec
            line = body_part
            if not line:
                continue

        # --- ordinary content line ---
        if pending_title is not None:
            current = Poem(title=_normalise_title(pending_title), section=section)
            pending_title = None
            if line:
                current.body.append(line)
            continue

        if current is not None:
            current.body.append(line)
        else:
            # The very first poem: its title is the first content line.
            current = Poem(title=_normalise_title(line), section=section)

    if current is not None:
        poems.append(current)

    # Drop fragments: poems with no real body (footnote continuations and
    # other extraction noise that slipped through as "titles"), and poems
    # whose title normalises to nothing but a footnote marker.
    poems = [
        p for p in poems
        if len(p.body) >= 3
        and p.title
        and not _FOOTNOTE_ONLY_RE.match(p.title)
        and not _BARE_YEAR_RE.match(p.title)
    ]

    # Exclude non-poetry sections (essays, addenda) from the atlas.
    poems = [
        p for p in poems
        if not any(
            kw in (p.section or "") for kw in config.EXCLUDED_SECTION_KEYWORDS
        )
    ]
    return poems
