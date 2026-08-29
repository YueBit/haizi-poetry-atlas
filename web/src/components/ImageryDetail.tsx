import { Link, useParams } from "react-router-dom";
import { useData } from "../App";
import { themeColor } from "../lib/theme";

export default function ImageryDetail() {
  const { word = "" } = useParams();
  const { imageryByWord, poemById } = useData();
  const node = imageryByWord.get(word);

  if (!node) {
    return (
      <div className="container section">
        <p className="lead">没有找到「{word}」这个意象。</p>
        <p className="muted">
          <Link to="/">← 回到图谱</Link>
        </p>
      </div>
    );
  }

  const color = themeColor(node.theme);
  const years = Object.keys(node.by_year).sort();
  const maxYear = Math.max(...years.map((y) => node.by_year[y]), 1);

  // Poems containing this word, with their occurrences of it.
  const poems = node.poem_ids
    .map((id) => poemById.get(id))
    .filter((p): p is NonNullable<typeof p> => Boolean(p))
    .sort((a, b) => (a.year ?? 0) - (b.year ?? 0));

  return (
    <div className="container section">
      <p className="eyebrow">
        <Link to="/">← 图谱</Link>
      </p>

      <div className="word-head" style={{ margin: "1.25rem 0 0.5rem" }}>
        <span className="word" style={{ color }}>
          {node.word}
        </span>
        <span
          className="theme-tag"
          style={{ color, borderColor: color }}
        >
          {node.theme_label}
        </span>
      </div>

      <div className="stat-row">
        <div className="stat">
          <span className="num">{node.frequency}</span>
          <span className="label">出现次数</span>
        </div>
        <div className="stat">
          <span className="num">{node.poem_count}</span>
          <span className="label">涉及诗篇</span>
        </div>
        <div className="stat">
          <span className="num">{node.related.length}</span>
          <span className="label">关联意象</span>
        </div>
      </div>

      {/* Timeline */}
      {years.length > 1 && (
        <>
          <h2 style={{ marginTop: "2.5rem", fontSize: "1.25rem" }}>
            时间上的分布
          </h2>
          <div className="timeline" role="img" aria-label="年份分布">
            {years.map((y) => (
              <div className="col" key={y} title={`${y} 年 · ${node.by_year[y]} 次`}>
                <span className="val">{node.by_year[y]}</span>
                <div
                  className="bar"
                  style={{
                    height: `${Math.max(6, (node.by_year[y] / maxYear) * 64)}px`,
                  }}
                />
                <span className="yr">{y}</span>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Related imagery */}
      <h2 style={{ marginTop: "2.5rem", fontSize: "1.25rem" }}>
        相近的意象
      </h2>
      <p className="muted" style={{ fontSize: "0.85rem" }}>
        得分 = 两词共同出现的诗篇数 ÷ √(各自出现诗篇数之积)，范围 0–1。
      </p>
      <ul className="related-list" style={{ marginTop: "0.75rem" }}>
        {node.related.map((r) => (
          <li className="related-item" key={r.word}>
            <Link className="word" to={`/imagery/${encodeURIComponent(r.word)}`}>
              {r.word}
            </Link>
            <span className="bar">
              <span style={{ width: `${r.score * 100}%` }} />
            </span>
            <span className="score">{r.score.toFixed(3)}</span>
          </li>
        ))}
      </ul>

      {/* Poems containing this word */}
      <h2 style={{ marginTop: "3rem", fontSize: "1.25rem" }}>
        出现于此的诗篇
      </h2>
      <p className="muted" style={{ fontSize: "0.85rem" }}>
        摘录仅为该词所在诗句的片段，非全诗。
      </p>
      {poems.map((p) => {
        const occ = p.occurrences.filter((o) => o.word === node.word);
        return (
          <article className="poem-card" key={p.id}>
            <h3 className="title">{p.title}</h3>
            <div className="meta">
              {p.year ? `${p.year} 年` : "年代不详"}
              {p.section ? ` · ${p.section.replace(/\u3000/g, " ")}` : ""}
            </div>
            {occ.slice(0, 4).map((o, i) => (
              <p className="occurrence" key={i}>
                <Highlight text={o.text} word={node.word} />
              </p>
            ))}
            {occ.length > 4 && (
              <p className="muted" style={{ fontSize: "0.8rem" }}>
                …另有 {occ.length - 4} 处
              </p>
            )}
          </article>
        );
      })}

      <p className="muted" style={{ marginTop: "2rem" }}>
        <Link to="/poems">在诗篇浏览器中查看全部 →</Link>
      </p>
    </div>
  );
}

function Highlight({ text, word }: { text: string; word: string }) {
  const idx = text.indexOf(word);
  if (idx === -1) return <>{text}</>;
  return (
    <>
      {text.slice(0, idx)}
      <mark>{word}</mark>
      {text.slice(idx + word.length)}
    </>
  );
}
