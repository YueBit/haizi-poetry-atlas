import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useData } from "../App";
import type { Poem } from "../types";

export default function PoemExplorer() {
  const { data, imageryByWord } = useData();
  const [query, setQuery] = useState("");
  const [word, setWord] = useState<string | null>(null);

  const words = useMemo(
    () => [...data.imagery].sort((a, b) => b.frequency - a.frequency),
    [data.imagery]
  );

  const results = useMemo(() => {
    let poems: Poem[] = data.poems;
    if (word) {
      poems = poems.filter((p) => p.imagery[word] !== undefined);
    } else if (query.trim()) {
      const q = query.trim();
      poems = poems.filter((p) => p.title.includes(q));
    }
    return poems.sort((a, b) => (a.year ?? 0) - (b.year ?? 0));
  }, [data.poems, word, query]);

  const matchedWord = query.trim() && imageryByWord.has(query.trim())
    ? imageryByWord.get(query.trim())!
    : null;

  return (
    <div className="container section">
      <h1 className="display" style={{ fontSize: "2rem" }}>
        诗篇
      </h1>
      <p className="lead" style={{ marginTop: "0.75rem" }}>
        从一个意象出发，回到诗本身。
      </p>

      <div style={{ margin: "2rem 0" }}>
        <input
          className="search-input"
          type="text"
          placeholder="搜索诗题，或输入一个意象（如「太阳」）"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            const w = e.target.value.trim();
            if (imageryByWord.has(w)) setWord(w);
            else if (!w) setWord(null);
          }}
        />
        {matchedWord && (
          <p className="muted" style={{ marginTop: "0.6rem", fontSize: "0.9rem" }}>
            「{matchedWord.word}」共出现在 {matchedWord.poem_count} 首诗篇中。{" "}
            <Link to={`/imagery/${encodeURIComponent(matchedWord.word)}`}>
              查看详情 →
            </Link>
          </p>
        )}
      </div>

      {/* Imagery word index */}
      <div style={{ margin: "1rem 0 2rem" }}>
        {words.map((n) => (
          <button
            key={n.word}
            className="word-chip"
            style={{
              background: "transparent",
              cursor: "pointer",
              fontSize: "0.92rem",
              ...(word === n.word
                ? { borderColor: "var(--accent)", color: "var(--accent)" }
                : {}),
            }}
            onClick={() => setWord(word === n.word ? null : n.word)}
          >
            {n.word}
          </button>
        ))}
      </div>

      {word && (
        <p className="muted" style={{ fontSize: "0.9rem" }}>
          正在查看含「<strong>{word}</strong>」的诗篇（{results.length} 首）·{" "}
          <button
            onClick={() => setWord(null)}
            style={{
              background: "none",
              border: "none",
              cursor: "pointer",
              color: "var(--accent)",
              fontFamily: "inherit",
            }}
          >
            清除
          </button>
        </p>
      )}

      <div style={{ marginTop: "1rem" }}>
        {results.length === 0 && (
          <p className="muted">没有匹配的诗篇。</p>
        )}
        {results.map((p) => (
          <article className="poem-card" key={p.id}>
            <h3 className="title">{p.title}</h3>
            <div className="meta">
              {p.year ? `${p.year} 年` : "年代不详"}
              {p.section ? ` · ${p.section.replace(/\u3000/g, " ")}` : ""}
            </div>

            {word ? (
              p.occurrences
                .filter((o) => o.word === word)
                .slice(0, 4)
                .map((o, i) => (
                  <p className="occurrence" key={i}>
                    <Highlight text={o.text} word={word} />
                  </p>
                ))
            ) : (
              <div style={{ marginTop: "0.6rem" }}>
                {Object.entries(p.imagery)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 8)
                  .map(([w]) => (
                    <Link
                      key={w}
                      className="word-chip"
                      to={`/imagery/${encodeURIComponent(w)}`}
                    >
                      {w}
                    </Link>
                  ))}
              </div>
            )}
          </article>
        ))}
      </div>
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
