import { createContext, useContext, useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import type { AtlasData } from "./types";
import { byId, byWord, loadData } from "./data";
import Nav from "./components/Nav";
import Atlas from "./components/Atlas";
import ImageryDetail from "./components/ImageryDetail";
import PoemExplorer from "./components/PoemExplorer";
import About from "./components/About";

export interface DataContextValue {
  data: AtlasData;
  imageryByWord: Map<string, AtlasData["imagery"][number]>;
  poemById: Map<string, AtlasData["poems"][number]>;
}

const DataContext = createContext<DataContextValue | null>(null);

export function useData(): DataContextValue {
  const ctx = useContext(DataContext);
  if (!ctx) throw new Error("useData must be used within <App/>");
  return ctx;
}

export default function App() {
  const [data, setData] = useState<AtlasData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  if (error) {
    return (
      <div className="center-screen">
        <p className="lead">数据加载失败。</p>
        <p className="muted">
          {error} — 请先运行 <code>python -m pipeline.run</code> 生成数据。
        </p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="center-screen">
        <p className="muted">正在展开海子的诗歌宇宙……</p>
      </div>
    );
  }

  const value: DataContextValue = {
    data,
    imageryByWord: byWord(data.imagery),
    poemById: byId(data.poems),
  };

  return (
    <DataContext.Provider value={value}>
      <Nav />
      <Routes>
        <Route path="/" element={<Atlas />} />
        <Route path="/imagery/:word" element={<ImageryDetail />} />
        <Route path="/poems" element={<PoemExplorer />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </DataContext.Provider>
  );
}
