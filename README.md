# 海子诗歌图谱 · Haizi Poetry Atlas

> Exploring recurring imagery and relationships in Hai Zi's poetry.
> 探索海子诗歌中反复出现的意象，以及它们彼此之间的关联。

**海子诗歌图谱** 是一个关于海子诗歌世界的数字人文项目。它把一本诗集转化为一张安静的、可交互的**意象图谱**，让你从一个词出发，回到诗本身。

**在线访问**：https://yuebit.github.io/haizi-poetry-atlas/

<!-- 截图占位：上线后替换为真实截图
![海子诗歌图谱](docs/screenshot.png)
-->

---

## 为什么做这个项目

2019 年夏天，我从茶卡盐湖开车向西，去德令哈。德令哈是海子《日记》写下的地方。从那里回来后，我一直好奇：海子的诗里，到底反复出现着哪些意象？它们之间又是怎样彼此关联的？

这个项目想回答的不是「哪些词出现得最多」，而是——

> **海子的诗看起来像什么？**

它更接近一张文学地图，而不是一个分析仪表盘。数据只是入口，阅读始终要回到诗。

## 可以探索什么

- **图谱（Atlas）** — 一张意象图谱。词的大小表示出现频率，连线表示意象之间的共现关系；点击一个词，进入它的世界。
- **意象（Imagery）** — 单个意象的详情：出现次数、涉及诗篇、时间分布、相近意象，以及它在具体诗句中的片段。
- **诗篇（Poems）** — 从一个意象出发，浏览包含它的诗篇，看到它出现的上下文。
- **关于（About）** — 项目的来处、方法与局限。

## 架构

```text
local poetry corpus → Python analysis pipeline → static JSON → static website
```

整个项目**没有后端、没有数据库**。分析在本地跑一次，产出静态 JSON，网站就是一个可以部署到任何静态托管（GitHub Pages 等）的前端。

```text
haizi-poetry-atlas/
├── corpus/               # 本地语料（不提交，见 corpus/README.md）
├── pipeline/             # Python 分析管线
│   ├── extract.py        #   PDF → 纯文本
│   ├── clean.py          #   清洗、规范化
│   ├── tokenize.py       #   jieba 分词（配意象词典）
│   ├── lexicon.py        #   手工整理的意象词表
│   ├── segmentation.py   #   切分诗篇
│   ├── imagery.py        #   意象统计
│   ├── cooccurrence.py   #   共现关系
│   ├── timeline.py       #   年份分布
│   ├── export.py         #   写出静态 JSON
│   └── run.py            #   一键入口
├── data/                 # 派生数据（提交：统计 + 短摘录）
│   ├── stats.json
│   ├── imagery.json
│   ├── cooccurrence.json
│   └── poems.json
├── web/                  # React + Vite + TypeScript + D3
└── requirements.txt
```

## 分析方法

方法刻意保持简单、透明：

- **分词** — 用 jieba，配一份手工整理的意象词表（天空、太阳、麦地、黑夜……）作为用户词典，保证「麦地」「黎明」这类词被当作整体。
- **频率** — 每个意象在全书中的出现次数，以及涉及的诗篇数。
- **共现 / 关联** — 两个意象的「关联得分」是它们的二值诗篇出现向量的余弦相似度：

  ```
  score(A, B) = |同时包含 A 和 B 的诗篇数| / sqrt(|含 A 的诗篇| × |含 B 的诗篇|)
  ```

  得分落在 0–1。它只说明「这两个意象常常出现在同一首诗里」，**不承载更多文学意义**——这个数字并不假装理解诗。

- **时间分布** — 按诗篇年份统计出现次数；年份无法确定的诗篇一律留空，不作猜测。

**已知局限**：诗篇的边界、标题与年份是从 PDF 文本中尽力提取的，存在偏差。长诗《太阳·七部书》结构复杂，切分尤其不完整。详见 About 页与 `corpus/README.md`。

## 本地运行

需要 Python 3.9+ 与 Node 18+。

```bash
# 1. 准备语料（见 corpus/README.md）

# 2. 运行分析管线，生成 data/*.json
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m pipeline.run

# 3. 构建网站
cd web
npm install
npm run build        # 产物在 web/dist/

# 或本地预览
npm run dev
```

## 语料准备

项目**不分发**海子诗作全文。分析管线是公开、可复现的；你只需按 `corpus/README.md` 的说明，把一份本地语料放入 `corpus/`，即可生成自己的图谱。

## 数据与版权

海子（查海生，1964–1989）的诗作仍在版权保护期内。因此：

- 仓库**不包含**诗作全文或 PDF；
- 公开的 `data/` 只包含**派生的统计、元数据与极短的诗句摘录**（约 36 字内），而非完整诗篇；
- 完整文本请自行获取，并仅用于个人研究。

## Roadmap

设计上已为以下方向留出空间（暂不实现）：

- **时间轴** — 意象随年份的演变；
- **地点** — 德令哈、青海、北京、昌平、黄河、长江……的地理维度；
- **诗歌指纹** — 用「自然 / 身体 / 死亡 / 家园 / 神话 / 光明」等维度刻画每首诗；
- **语义搜索** — 用 embeddings 搜索「离开故乡」这类主题；
- **相似诗篇** — 按意象或语义结构找到相近的诗。

不会把 AI 聊天机器人作为核心功能。
