"""Curated imagery lexicon.

The atlas is not a raw word-frequency table; it is a hand-curated set of the
images and motifs that recur throughout Hai Zi's poetry. This list combines:

  * the imagery the project explicitly cares about (天空 太阳 麦地 …),
  * words that jieba's TF-IDF keyword extraction surfaced as genuinely
    frequent in the corpus (from the original experiment), with editorial
    noise (一只 坐在 我要 …) and meta-language (诗歌 诗人) removed.

Each word is assigned a single *theme* — an editorial grouping used for
colour-coding and for the future "poem fingerprint" feature. The grouping is
interpretive, not scientific, and is documented as such in the README.

The full list is also exported as a jieba *user dictionary* so that multi-
character images such as 麦地 / 黑夜 / 黎明 are segmented as single tokens
rather than split into parts.
"""

from __future__ import annotations

# word -> theme. Order matters only for the generated dictionary file.
LEXICON: dict[str, str] = {
    # 自然 · nature
    "天空": "nature",
    "太阳": "nature",
    "大地": "nature",
    "麦地": "nature",
    "月亮": "nature",
    "草原": "nature",
    "河流": "nature",
    "石头": "nature",
    "青草": "nature",
    "大海": "nature",
    "火焰": "nature",
    "野花": "nature",
    "沙漠": "nature",
    "岩石": "nature",
    "土地": "nature",
    "花朵": "nature",
    "豹子": "nature",
    "森林": "nature",
    "泥土": "nature",
    "山谷": "nature",
    "山峰": "nature",
    "雨水": "nature",
    "雪花": "nature",
    "星星": "nature",
    "阳光": "nature",
    "月光": "nature",
    "风": "nature",
    "山": "nature",
    "海": "nature",
    "火": "nature",
    "云": "nature",
    # 身体 · body
    "头颅": "body",
    "肉体": "body",
    "身体": "body",
    "眼睛": "body",
    "嘴唇": "body",
    "手": "body",
    "血液": "body",
    "骨头": "body",
    "心脏": "body",
    "皮肤": "body",
    "头发": "body",
    "脸": "body",
    "泪水": "body",
    # 死亡 · death
    "死亡": "death",
    "死去": "death",
    "坟墓": "death",
    "尸体": "death",
    "孤独": "death",
    "痛苦": "death",
    "饥饿": "death",
    "黑暗": "death",
    # 家园 · home
    "村庄": "home",
    "故乡": "home",
    "母亲": "home",
    "父亲": "home",
    "儿子": "home",
    "兄弟": "home",
    "女儿": "home",
    "少女": "home",
    "姐姐": "home",
    "家": "home",
    "房屋": "home",
    # 神话 · myth
    "众神": "myth",
    "神灵": "myth",
    "上帝": "myth",
    "天堂": "myth",
    "王子": "myth",
    "公主": "myth",
    "国王": "myth",
    "宫殿": "myth",
    "灵魂": "myth",
    "幻象": "myth",
    "宝剑": "myth",
    "王": "myth",
    # 光明与时间 · light & time
    "黑夜": "light",
    "黎明": "light",
    "黄昏": "light",
    "夜晚": "light",
    "春天": "light",
    "秋天": "light",
    "冬天": "light",
    "夏天": "light",
    "火把": "light",
    "燃烧": "light",
    "照亮": "light",
    "光明": "light",
    "曙光": "light",
    # 地理 · place
    "德令哈": "place",
    "青海": "place",
    "北京": "place",
    "昌平": "place",
    "黄河": "place",
    "长江": "place",
    "北方": "place",
    "南方": "place",
    "东方": "place",
    "西方": "place",
    "远方": "place",
}

# Ordering used for stable, reproducible output (ranked by frequency later,
# but this provides a deterministic tiebreak).
THEME_ORDER = ["nature", "light", "home", "body", "death", "myth", "place"]

THEME_LABELS: dict[str, str] = {
    "nature": "自然",
    "light": "光明",
    "home": "家园",
    "body": "身体",
    "death": "死亡",
    "myth": "神话",
    "place": "地理",
}


def build_user_dict(freq: int = 200000) -> str:
    """Return jieba user-dictionary text, one ``word freq`` line each.

    A deliberately high frequency forces jieba to treat each lexicon word as
    a single token even when its parts are themselves common words.
    """
    return "\n".join(f"{w} {freq}" for w in LEXICON) + "\n"
